"""Z.AI Chat Completions adapter: OpenAI SDK with base_url swap, reasoning_content streaming, preserved thinking (IS-11, DD-04).

Uses the standard OpenAI Chat Completions API against https://api.z.ai/api/paas/v4/.
Z.AI-specific parameters (thinking, reasoning_effort) are passed via extra_body.
reasoning_content streams as thinking deltas; clear_thinking=false preserves reasoning across turns.
Usage normalization: input_tokens INCLUDES cached tokens (OpenAI native behavior) - matches the cost.py contract.
"""
import asyncio, datetime, json
from pathlib import Path
from typing import AsyncIterator, Optional
import openai
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage
from lana.providers.base import PROVIDER_TIMEOUT, RETRY_DELAYS_SECONDS, AdapterDelta, ProviderError, is_retryable_error

ZAI_BASE_URL = "https://api.z.ai/api/paas/v4/"


def dump_debug(debug_dir: Optional[Path], name: str, payload: dict) -> None:
  if debug_dir is None: return
  stamp = datetime.datetime.now().strftime("%H%M%S_%f")
  (debug_dir / f"zai_{stamp}_{name}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# Canonical messages -> Chat Completions format; system goes into messages array (not separate param)
# Z.AI preserved thinking: reasoning_content from prior turns is resent in the assistant message (clear_thinking=false)
def build_messages(system: str, messages: list[Message]) -> list[dict]:
  result: list[dict] = [{"role": "system", "content": system}]
  for message in messages:
    if message.role == "system": continue
    if message.role == "user":
      result.append({"role": "user", "content": message.content})
    elif message.role == "assistant":
      msg: dict = {"role": "assistant"}
      zai_reasoning = ""
      for thinking in message.thinking:
        if thinking.provider == "zai":
          zai_reasoning += thinking.payload.get("reasoning_content", "")
      if zai_reasoning: msg["reasoning_content"] = zai_reasoning
      if message.content: msg["content"] = message.content
      if message.tool_calls:
        msg["tool_calls"] = [{"id": call.id, "type": "function", "function": {"name": call.name, "arguments": call.args_json}} for call in message.tool_calls]
      result.append(msg)
    elif message.role == "tool":
      result.append({"role": "tool", "tool_call_id": message.tool_call_id, "content": message.content})
  return result


def build_tools(tools: list[dict]) -> list[dict]:
  return [{"type": "function", "function": {"name": tool["name"], "description": tool["description"], "parameters": tool["schema"]}} for tool in tools]


def build_request_params(role: ResolvedRole) -> dict:
  params: dict = {"max_tokens": role.max_output}
  extra_body: dict = {}
  if role.method == "reasoning_effort":
    extra_body["reasoning_effort"] = role.params["reasoning_effort"]
    extra_body["thinking"] = {"type": "enabled", "clear_thinking": False}
  elif role.method == "thinking":
    thinking_on = role.params.get("thinking_budget", 0) > 0
    extra_body["thinking"] = {"type": "enabled" if thinking_on else "disabled", "clear_thinking": False}
  if extra_body: params["extra_body"] = extra_body
  return params


def normalize_usage(usage) -> Usage:
  cached = 0
  details = getattr(usage, "prompt_tokens_details", None)
  if details is not None: cached = getattr(details, "cached_tokens", 0) or 0
  return Usage(input_tokens=getattr(usage, "prompt_tokens", 0) or 0, output_tokens=getattr(usage, "completion_tokens", 0) or 0, cache_read_tokens=cached)


class ZAIAdapter:
  def __init__(self, api_key: str, debug_dir: Optional[Path] = None):
    self.client = openai.AsyncOpenAI(api_key=api_key, base_url=ZAI_BASE_URL, timeout=PROVIDER_TIMEOUT, max_retries=0)  # FR-16 BL-05: Lana owns retries (UX-03)
    self.debug_dir = debug_dir

  def supports_web_search(self) -> bool:
    return False

  # FR-16 UX-03: retry retryable SDK failures BEFORE the first streamed delta, each announced as a notice delta
  async def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]:
    request = {"model": role.model_id, "messages": build_messages(system, messages), "stream": True, "stream_options": {"include_usage": True}, **build_request_params(role)}
    if tools: request["tools"] = build_tools(tools)
    dump_debug(self.debug_dir, "request", {key: value for key, value in request.items() if key != "stream"})
    attempt = 0
    while True:
      yielded = False
      try:
        async for delta in self._stream_once(request):
          yielded = True
          yield delta
        return
      except ProviderError:
        raise
      except openai.OpenAIError as error:
        if not yielded and attempt < len(RETRY_DELAYS_SECONDS) and is_retryable_error(error):
          delay = RETRY_DELAYS_SECONDS[attempt]
          attempt += 1
          yield AdapterDelta(kind="notice", text=f"Z.AI {type(error).__name__} - retrying in {delay:.0f}s (attempt {attempt}/{len(RETRY_DELAYS_SECONDS)})...")
          await asyncio.sleep(delay)
          continue
        raise ProviderError(f"Z.AI API error: {error}") from None

  async def _stream_once(self, request: dict) -> AsyncIterator[AdapterDelta]:
    stream = await self.client.chat.completions.create(**request)
    try:
      reasoning_content = ""
      tool_calls_acc: dict[int, dict] = {}
      final_usage = None
      async for chunk in stream:
        if not chunk.choices:
          if hasattr(chunk, "usage") and chunk.usage:
            final_usage = chunk.usage
          continue
        delta = chunk.choices[0].delta
        # Thinking content (Z.AI-specific reasoning_content field)
        rc = getattr(delta, "reasoning_content", None)
        if rc:
          reasoning_content += rc
          yield AdapterDelta(kind="thinking", text=rc)
        # Text content
        if delta.content:
          yield AdapterDelta(kind="text", text=delta.content)
        # Tool calls (accumulated by index, emitted at end)
        if hasattr(delta, "tool_calls") and delta.tool_calls:
          for tc in delta.tool_calls:
            idx = tc.index
            if idx not in tool_calls_acc: tool_calls_acc[idx] = {"id": "", "name": "", "arguments": ""}
            if tc.id: tool_calls_acc[idx]["id"] = tc.id
            if hasattr(tc, "function") and tc.function:
              if tc.function.name: tool_calls_acc[idx]["name"] = tc.function.name
              if tc.function.arguments: tool_calls_acc[idx]["arguments"] += tc.function.arguments
        # Usage in final chunk
        if hasattr(chunk, "usage") and chunk.usage:
          final_usage = chunk.usage
      # Emit thinking block for resend (preserved thinking with clear_thinking=false)
      if reasoning_content:
        yield AdapterDelta(kind="thinking", text="", thinking=ThinkingBlock(provider="zai", payload={"reasoning_content": reasoning_content}))
      # Emit accumulated tool calls
      for idx in sorted(tool_calls_acc):
        tc = tool_calls_acc[idx]
        call_id = tc["id"] or f"call_{idx}"
        yield AdapterDelta(kind="tool_call", tool_call=ToolCall(id=call_id, name=tc["name"], args_json=tc["arguments"] or "{}"))
      if final_usage is not None:
        yield AdapterDelta(kind="usage", usage=normalize_usage(final_usage))
      response_debug = {"reasoning_content": reasoning_content, "tool_calls": [tool_calls_acc[i] for i in sorted(tool_calls_acc)]}
      response_debug["usage"] = final_usage.model_dump() if final_usage and hasattr(final_usage, "model_dump") else str(final_usage)
      dump_debug(self.debug_dir, "response", response_debug)
    finally:
      await stream.close()
