"""Anthropic Messages API adapter: thinking resend, cache_control breakpoints + automatic caching (LANAAGNT-FR-06, IS-12).

Cache layout (NFR-03): cache_control on the last tool definition and on the system block (explicit prefix
breakpoints) plus top-level automatic caching so growing history is cache-read too.
Usage normalization: input_tokens is reported EXCLUDING cache reads by Anthropic - we normalize to
input_tokens INCLUDING cache reads to match the cost.py contract.
"""
import asyncio, datetime, json
from pathlib import Path
from typing import AsyncIterator, Optional
import anthropic
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage
from lana.providers.base import PROVIDER_TIMEOUT, RETRY_DELAYS_SECONDS, AdapterDelta, ProviderError, is_retryable_error

EPHEMERAL = {"type": "ephemeral"}


def dump_debug(debug_dir: Optional[Path], name: str, payload: dict) -> None:
  if debug_dir is None: return
  stamp = datetime.datetime.now().strftime("%H%M%S_%f")
  (debug_dir / f"anthropic_{stamp}_{name}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# Canonical messages -> Messages API format; consecutive tool results merge into one user message (alternation rule)
def build_messages(messages: list[Message]) -> list[dict]:
  result: list[dict] = []
  for message in messages:
    if message.role == "system": continue
    if message.role == "user":
      result.append({"role": "user", "content": [{"type": "text", "text": message.content}]})
    elif message.role == "assistant":
      blocks: list[dict] = []
      for thinking in message.thinking:
        if thinking.provider == "anthropic": blocks.append(thinking.payload)  # thinking blocks resent unchanged (signature integrity)
      if message.content: blocks.append({"type": "text", "text": message.content})
      for call in message.tool_calls:
        try:
          parsed_args = call.args()
        except ValueError:
          parsed_args = {}
        blocks.append({"type": "tool_use", "id": call.id, "name": call.name, "input": parsed_args})
      if blocks: result.append({"role": "assistant", "content": blocks})
    elif message.role == "tool":
      block = {"type": "tool_result", "tool_use_id": message.tool_call_id, "content": message.content}
      if result and result[-1]["role"] == "user" and result[-1]["content"] and result[-1]["content"][0].get("type") == "tool_result":
        result[-1]["content"].append(block)
      else:
        result.append({"role": "user", "content": [block]})
  return result


# Tools array with cache_control breakpoint on the LAST tool (prefix order: tools -> system -> messages)
def build_tools(tools: list[dict]) -> list[dict]:
  rendered = [{"name": tool["name"], "description": tool["description"], "input_schema": tool["schema"]} for tool in tools]
  if rendered: rendered[-1]["cache_control"] = EPHEMERAL
  return rendered


def build_request_params(role: ResolvedRole) -> dict:
  params: dict = {"max_tokens": role.max_output}
  extra_body: dict = {"cache_control": EPHEMERAL}  # top-level automatic caching for growing history (FR-06)
  if role.method == "thinking":
    budget = role.params.get("thinking_budget", 0)
    if budget >= 1024:
      params["thinking"] = {"type": "enabled", "budget_tokens": budget}
      params["max_tokens"] = max(role.max_output, budget + 2048)  # budget must stay below max_tokens
  elif role.method == "adaptive_thinking":
    params["thinking"] = {"type": "adaptive"}
    extra_body["output_config"] = {"effort": role.params.get("effort", "medium")}
  elif role.method == "effort":
    extra_body["output_config"] = {"effort": role.params.get("effort", "medium")}
  elif role.method == "temperature":
    params["temperature"] = role.params.get("temperature", 0.0)
  params["extra_body"] = extra_body
  return params


def normalize_usage(usage) -> Usage:
  cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
  cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
  plain_input = getattr(usage, "input_tokens", 0) or 0
  return Usage(input_tokens=plain_input + cache_read + cache_write, output_tokens=getattr(usage, "output_tokens", 0) or 0, cache_read_tokens=cache_read, cache_write_tokens=cache_write)


class AnthropicAdapter:
  def __init__(self, api_key: str, debug_dir: Optional[Path] = None):
    self.client = anthropic.AsyncAnthropic(api_key=api_key, timeout=PROVIDER_TIMEOUT, max_retries=0)  # FR-16 BL-05: Lana owns retries (UX-03)
    self.sync_client = anthropic.Anthropic(api_key=api_key, timeout=PROVIDER_TIMEOUT, max_retries=0)
    self.debug_dir = debug_dir

  def supports_web_search(self) -> bool:
    return True

  # FR-16 UX-03: retry retryable SDK failures BEFORE the first streamed delta, each announced as a notice delta
  async def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]:
    request = {"model": role.model_id, "system": [{"type": "text", "text": system, "cache_control": EPHEMERAL}], "messages": build_messages(messages), **build_request_params(role)}
    if tools: request["tools"] = build_tools(tools)
    if role.beta: request.setdefault("extra_headers", {})["anthropic-beta"] = role.beta
    dump_debug(self.debug_dir, "request", {key: value for key, value in request.items() if key != "extra_headers"})
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
      except anthropic.AnthropicError as error:
        if not yielded and attempt < len(RETRY_DELAYS_SECONDS) and is_retryable_error(error):
          delay = RETRY_DELAYS_SECONDS[attempt]
          attempt += 1
          yield AdapterDelta(kind="notice", text=f"Anthropic {type(error).__name__} - retrying in {delay:.0f}s (attempt {attempt}/{len(RETRY_DELAYS_SECONDS)})...")
          await asyncio.sleep(delay)
          continue
        raise ProviderError(f"Anthropic API error: {error}") from None

  async def _stream_once(self, request: dict) -> AsyncIterator[AdapterDelta]:
    async with self.client.messages.stream(**request) as stream:
      async for event in stream:
        event_type = getattr(event, "type", "")
        if event_type == "content_block_delta":
          delta = event.delta
          delta_type = getattr(delta, "type", "")
          if delta_type == "text_delta": yield AdapterDelta(kind="text", text=delta.text)
          elif delta_type == "thinking_delta": yield AdapterDelta(kind="thinking", text=delta.thinking)
      final = await stream.get_final_message()
    dump_debug(self.debug_dir, "response", final.model_dump() if hasattr(final, "model_dump") else {"raw": str(final)})
    for block in final.content:
      block_type = getattr(block, "type", "")
      if block_type in ("thinking", "redacted_thinking"):
        payload = block.model_dump() if hasattr(block, "model_dump") else dict(block)
        yield AdapterDelta(kind="thinking", text="", thinking=ThinkingBlock(provider="anthropic", payload=payload))
      elif block_type == "tool_use":
        yield AdapterDelta(kind="tool_call", tool_call=ToolCall(id=block.id, name=block.name, args_json=json.dumps(block.input, ensure_ascii=False)))
    yield AdapterDelta(kind="usage", usage=normalize_usage(final.usage))

  # One-shot provider-native web search for the websearch role (FR-13); sync - callable from tool executors
  def run_web_search(self, query: str, domain: Optional[str], role: ResolvedRole) -> list[dict]:
    tool: dict = {"type": "web_search_20250305", "name": "web_search", "max_uses": 1}  # allowed_domains is web_fetch-only (IN24, BG-0003)
    prompt = f"Search the web for: {query}" + (f" (restrict to site {domain})" if domain else "")
    try:
      response = self.sync_client.messages.create(model=role.model_id, max_tokens=min(role.max_output, 2048), messages=[{"role": "user", "content": prompt}], tools=[tool])
    except anthropic.AnthropicError as error:
      raise ProviderError(f"Anthropic web search failed: {error}") from None
    results, text_parts = [], []
    for block in response.content:
      block_type = getattr(block, "type", "")
      if block_type == "web_search_tool_result":
        for entry in getattr(block, "content", []) or []:
          if getattr(entry, "type", "") == "web_search_result":
            results.append({"title": getattr(entry, "title", ""), "url": getattr(entry, "url", ""), "summary": (getattr(entry, "page_age", "") or "")})
      elif block_type == "text": text_parts.append(block.text)
    summary_text = " ".join(text_parts)[:300]
    for result in results:
      if not result["summary"]: result["summary"] = summary_text
    if not results: results.append({"title": "Web search response", "url": "", "summary": summary_text})
    return results
