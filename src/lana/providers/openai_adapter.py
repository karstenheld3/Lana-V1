"""OpenAI Responses API adapter: typed output parsing, reasoning passthrough, web_search side-call (LANAAGNT-FR-06, IS-11, DD-04).

Never reads only the first output item - the output array is parsed typed (message | reasoning | function_call).
store=false; reasoning items are captured as ThinkingBlocks and resent verbatim on the next call of the tool loop.
Usage normalization: input_tokens INCLUDES cached tokens (OpenAI native behavior) - matches the cost.py contract.
"""
import asyncio, datetime, json, uuid
from pathlib import Path
from typing import AsyncIterator, Optional
import openai
from lana.config import ResolvedRole
from lana.models import Message, ThinkingBlock, ToolCall, Usage
from lana.providers.base import PROVIDER_TIMEOUT, RETRY_DELAYS_SECONDS, AdapterDelta, ProviderError, is_retryable_error


def dump_debug(debug_dir: Optional[Path], name: str, payload: dict) -> None:
  if debug_dir is None: return
  stamp = datetime.datetime.now().strftime("%H%M%S_%f")
  (debug_dir / f"openai_{stamp}_{name}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# Canonical messages -> Responses input item array (system goes into instructions, not here)
def build_input_items(messages: list[Message]) -> list[dict]:
  items: list[dict] = []
  for message in messages:
    if message.role == "system": continue
    if message.role == "user": items.append({"role": "user", "content": message.content})
    elif message.role == "assistant":
      for thinking in message.thinking:
        if thinking.provider == "openai": items.append(thinking.payload)  # reasoning items resent verbatim (RF-01)
      if message.content: items.append({"role": "assistant", "content": message.content})
      for call in message.tool_calls: items.append({"type": "function_call", "call_id": call.id, "name": call.name, "arguments": call.args_json})
    elif message.role == "tool": items.append({"type": "function_call_output", "call_id": message.tool_call_id, "output": message.content})
  return items


def build_tools(tools: list[dict]) -> list[dict]:
  return [{"type": "function", "name": tool["name"], "description": tool["description"], "parameters": tool["schema"]} for tool in tools]


def build_request_params(role: ResolvedRole) -> dict:
  params: dict = {"max_output_tokens": role.max_output}
  if role.method == "temperature": params["temperature"] = role.params["temperature"]
  elif role.method == "reasoning_effort":
    params["reasoning"] = {"effort": role.params["reasoning_effort"]}
    params["include"] = ["reasoning.encrypted_content"]  # resendable reasoning with store=false
  return params


def normalize_usage(usage) -> Usage:
  cached = 0
  details = getattr(usage, "input_tokens_details", None) or getattr(usage, "prompt_tokens_details", None)
  if details is not None: cached = getattr(details, "cached_tokens", 0) or 0
  return Usage(input_tokens=usage.input_tokens or 0, output_tokens=usage.output_tokens or 0, cache_read_tokens=cached)


class OpenAIAdapter:
  def __init__(self, api_key: str, debug_dir: Optional[Path] = None):
    self.client = openai.AsyncOpenAI(api_key=api_key, timeout=PROVIDER_TIMEOUT, max_retries=0)  # FR-16 BL-05: Lana owns retries (UX-03)
    self.sync_client = openai.OpenAI(api_key=api_key, timeout=PROVIDER_TIMEOUT, max_retries=0)
    self.debug_dir = debug_dir

  def supports_web_search(self) -> bool:
    return True

  # FR-16 UX-03: retry retryable SDK failures BEFORE the first streamed delta, each announced as a notice delta
  async def stream_turn(self, system: str, tools: list[dict], messages: list[Message], role: ResolvedRole) -> AsyncIterator[AdapterDelta]:
    request = {"model": role.model_id, "instructions": system, "input": build_input_items(messages), "store": False, "stream": True, **build_request_params(role)}
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
        raise  # already normalized (response.failed, incomplete stream) - never retried
      except openai.OpenAIError as error:
        if not yielded and attempt < len(RETRY_DELAYS_SECONDS) and is_retryable_error(error):
          delay = RETRY_DELAYS_SECONDS[attempt]
          attempt += 1
          yield AdapterDelta(kind="notice", text=f"OpenAI {type(error).__name__} - retrying in {delay:.0f}s (attempt {attempt}/{len(RETRY_DELAYS_SECONDS)})...")
          await asyncio.sleep(delay)
          continue
        raise ProviderError(f"OpenAI API error: {error}") from None

  async def _stream_once(self, request: dict) -> AsyncIterator[AdapterDelta]:
    stream = await self.client.responses.create(**request)
    final = None
    async for event in stream:
      event_type = getattr(event, "type", "")
      if event_type == "response.output_text.delta": yield AdapterDelta(kind="text", text=event.delta)
      elif event_type == "response.reasoning_summary_text.delta": yield AdapterDelta(kind="thinking", text=event.delta)
      elif event_type == "response.completed": final = event.response
      elif event_type == "response.failed":
        error_detail = getattr(getattr(event.response, "error", None), "message", "response.failed")
        raise ProviderError(f"OpenAI response failed: {error_detail}")
    if final is None: raise ProviderError("OpenAI stream ended without response.completed")
    dump_debug(self.debug_dir, "response", final.model_dump() if hasattr(final, "model_dump") else {"raw": str(final)})
    for item in final.output:  # typed array parsing - message | reasoning | function_call (RF-01)
      item_type = getattr(item, "type", "")
      if item_type == "reasoning":
        payload = item.model_dump() if hasattr(item, "model_dump") else dict(item)
        yield AdapterDelta(kind="thinking", text="", thinking=ThinkingBlock(provider="openai", payload=payload))
      elif item_type == "function_call":
        call_id = getattr(item, "call_id", None) or getattr(item, "id", None) or f"call_{uuid.uuid4().hex[:8]}"
        yield AdapterDelta(kind="tool_call", tool_call=ToolCall(id=call_id, name=item.name, args_json=item.arguments or "{}"))
    if final.usage is not None: yield AdapterDelta(kind="usage", usage=normalize_usage(final.usage))

  # One-shot provider-native web search for the websearch role (FR-13); sync - callable from tool executors
  def run_web_search(self, query: str, domain: Optional[str], role: ResolvedRole) -> list[dict]:
    prompt = f"Search the web for: {query}" + (f" (restrict to site {domain})" if domain else "")
    try:
      response = self.sync_client.responses.create(model=role.model_id, input=prompt, tools=[{"type": "web_search"}], store=False)
    except openai.OpenAIError as error:
      raise ProviderError(f"OpenAI web search failed: {error}") from None
    text = getattr(response, "output_text", "") or ""
    results, seen_urls = [], set()
    for item in response.output:
      if getattr(item, "type", "") != "message": continue
      for content in getattr(item, "content", []) or []:
        for annotation in getattr(content, "annotations", []) or []:
          if getattr(annotation, "type", "") == "url_citation" and annotation.url not in seen_urls:
            seen_urls.add(annotation.url)
            results.append({"title": getattr(annotation, "title", "") or annotation.url, "url": annotation.url, "summary": text[:300]})
    if not results: results.append({"title": "Web search response", "url": "", "summary": text[:300]})
    return results
