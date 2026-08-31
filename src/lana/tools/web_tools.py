"""Web research tools: search_web (websearch role side-call), read_url_content, view_content_chunk (LANAAGNT-FR-13, IS-18).

read_url_content is plain HTTP fetching (no LLM backend); the approval gate runs in the agent before dispatch.
Chunk store: in-memory + mirrored to <data_dir>/chunks/<document_id>.json so view_content_chunk survives --resume.
"""
import html.parser, json, time, urllib.error, urllib.request, uuid
from pathlib import Path
from lana.debuglog import dlog
from lana.providers import get_adapter
from lana.tools import ToolContext, ToolError

FETCH_MAX_BYTES = 5 * 1024 * 1024  # EC-18
CHUNK_CHARS = 5000  # [ASSUMED - matches Cascade's observed 2-8 KB chunk cost range]
FETCH_TIMEOUT_SECONDS = 30
FETCH_WALL_DEADLINE_SECONDS = 120  # FR-16 BL-07: total transfer bound - a trickling server cannot extend a fetch past it
FETCH_CHUNK_BYTES = 65536
TEXT_CONTENT_MARKERS = ("text/", "application/json", "application/xml", "application/xhtml")


class _HtmlTextExtractor(html.parser.HTMLParser):
  SKIP_TAGS = ("script", "style", "noscript", "head", "svg")

  def __init__(self):
    super().__init__()
    self.parts: list[str] = []
    self.skip_depth = 0

  def handle_starttag(self, tag, attrs):
    if tag in self.SKIP_TAGS: self.skip_depth += 1

  def handle_endtag(self, tag):
    if tag in self.SKIP_TAGS and self.skip_depth: self.skip_depth -= 1

  def handle_data(self, data):
    if not self.skip_depth and data.strip(): self.parts.append(data.strip())


def html_to_text(raw: str) -> str:
  extractor = _HtmlTextExtractor()
  extractor.feed(raw)
  return "\n".join(extractor.parts)


def chunk_text(text: str) -> list[str]:
  return [text[start:start + CHUNK_CHARS] for start in range(0, len(text), CHUNK_CHARS)] or [""]


def chunks_dir(context: ToolContext) -> Path:
  return (context.data_dir or Path(context.workspace) / ".lana-data") / "chunks"


def store_chunks(context: ToolContext, document_id: str, chunks: list[str]) -> None:
  context.chunk_store[document_id] = chunks
  target_dir = chunks_dir(context)
  target_dir.mkdir(parents=True, exist_ok=True)
  (target_dir / f"{document_id}.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")


def load_chunks(context: ToolContext, document_id: str) -> list[str] | None:
  if document_id in context.chunk_store: return context.chunk_store[document_id]
  on_disk = chunks_dir(context) / f"{document_id}.json"
  if on_disk.exists():
    chunks = json.loads(on_disk.read_text(encoding="utf-8"))
    context.chunk_store[document_id] = chunks
    return chunks
  return None


# ----------------------------------------- START: read_url_content / view_content_chunk --------------------------------------

def execute_read_url_content(args: dict, context: ToolContext) -> str:
  url = args["Url"]
  if not url.lower().startswith(("http://", "https://")): raise ToolError(f"URL must be HTTP or HTTPS: '{url}'")
  request = urllib.request.Request(url, headers={"User-Agent": "Lana"})
  try:
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
      content_type = response.headers.get("Content-Type", "")
      if content_type and not any(marker in content_type.lower() for marker in TEXT_CONTENT_MARKERS):
        raise ToolError(f"Refused non-text content from '{url}': Content-Type '{content_type}' (EC-18)")
      body = b""
      wall_deadline = time.monotonic() + FETCH_WALL_DEADLINE_SECONDS  # FR-16 BL-07: chunked read under a wall-clock bound
      while len(body) <= FETCH_MAX_BYTES:
        chunk = response.read(FETCH_CHUNK_BYTES)
        if not chunk: break
        body += chunk
        if time.monotonic() > wall_deadline:
          raise ToolError(f"Fetch of '{url}' aborted after {FETCH_WALL_DEADLINE_SECONDS} s wall-clock deadline ({len(body)} bytes received) - the server is too slow (BL-07)")
  except ToolError:
    raise
  except urllib.error.URLError as error:
    raise ToolError(f"Cannot fetch '{url}': {error.reason if hasattr(error, 'reason') else error}") from None
  except OSError as error:
    raise ToolError(f"Cannot fetch '{url}': {error}") from None
  if len(body) > FETCH_MAX_BYTES: raise ToolError(f"Refused '{url}': body exceeds {FETCH_MAX_BYTES // (1024 * 1024)} MB (EC-18)")
  if b"\x00" in body[:1024]: raise ToolError(f"Refused binary content from '{url}' (EC-18)")
  raw = body.decode("utf-8", errors="replace")
  text = html_to_text(raw) if "<html" in raw[:2000].lower() or "text/html" in content_type else raw
  chunks = chunk_text(text)
  document_id = f"doc_{uuid.uuid4().hex[:8]}"
  store_chunks(context, document_id, chunks)
  total = len(chunks)
  header = f"Document '{document_id}' fetched from {url}: {total} chunk" + ("s" if total != 1 else "") + f" of up to {CHUNK_CHARS} chars. Use view_content_chunk with positions 1..{total} for more.\n\n"
  return header + f"[chunk 1 of {total}]\n{chunks[0]}"


def execute_view_content_chunk(args: dict, context: ToolContext) -> str:
  document_id, position = args["document_id"], args["position"]
  chunks = load_chunks(context, document_id)
  if chunks is None: raise ToolError(f"Unknown document_id '{document_id}'. Fetch the URL with read_url_content first.")
  if not 1 <= position <= len(chunks): raise ToolError(f"Position {position} out of range for '{document_id}': valid range is 1..{len(chunks)} (EC-25)")
  return f"[chunk {position} of {len(chunks)}]\n{chunks[position - 1]}"

# ----------------------------------------- END: read_url_content / view_content_chunk ----------------------------------------


# ----------------------------------------- START: search_web -----------------------------------------------------------------

# Render Cascade's documented 5-result format (FR-13)
def render_search_results(results: list[dict]) -> str:
  lines = []
  for result in results[:5]:
    summary = (result.get("summary") or "")[:300]
    lines.append(f"- {result.get('title', '(no title)')}\n  {result.get('url', '')}\n  {summary}")
  lines.append("\nUse read_url_content on a result URL to read further.")
  return "\n".join(lines)


def execute_search_web(args: dict, context: ToolContext) -> str:
  app = context.app_config
  if app is None: raise ToolError("search_web unavailable: no app configuration on the tool context.")
  role = app.roles.get("websearch")
  if role is None: raise ToolError("search_web unavailable: no 'websearch' role configured in lana-config.json.")
  adapter = get_adapter(role, app)
  if not adapter.supports_web_search(): raise ToolError(f"search_web unavailable: provider adapter for '{role.model_id}' has no web search support. Configure a different websearch model (EC-19).")
  started_at = time.perf_counter()  # LANADEBG-FR-02: sidecall latency; usage is not surfaced by provider web-search wrappers
  results = adapter.run_web_search(args["query"], args.get("domain"), role)
  dlog("llm", "sidecall", role="websearch", provider=role.provider, model=role.model_id, dur_ms=int((time.perf_counter() - started_at) * 1000), results=len(results))
  return render_search_results(results)

# ----------------------------------------- END: search_web -------------------------------------------------------------------
