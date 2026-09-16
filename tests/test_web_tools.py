"""TK-028/029: web tools against a local fixture server (IP01 TC-44 offline parts, TC-45; TC-43 live)."""
import http.server, os, threading
import pytest
from lana.tools import ToolContext, ToolError
from lana.tools.web_tools import CHUNK_CHARS, chunk_text, execute_read_url_content, execute_search_web, execute_view_content_chunk, html_to_text, render_search_results

HTML_PAGE = "<html><head><title>T</title><script>ignored()</script><style>.x{}</style></head><body><h1>Heading</h1><p>Paragraph one.</p><p>" + ("Long text. " * 1200) + "</p></body></html>"


class FixtureHandler(http.server.BaseHTTPRequestHandler):
  def log_message(self, *args): pass

  def do_GET(self):
    if self.path == "/page.html": self.reply(200, "text/html", HTML_PAGE.encode("utf-8"))
    elif self.path == "/plain.txt": self.reply(200, "text/plain", b"plain body")
    elif self.path == "/huge.txt": self.reply(200, "text/plain", b"X" * (5 * 1024 * 1024 + 100))
    elif self.path == "/binary.bin": self.reply(200, "text/plain", b"\x00\x01\x02" * 100)  # binary sneaking behind a text header
    elif self.path == "/image.png": self.reply(200, "image/png", b"\x89PNG fake")
    else: self.reply(404, "text/plain", b"not found")

  def reply(self, status, content_type, body):
    self.send_response(status)
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)


@pytest.fixture(scope="module")
def fixture_server():
  server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  yield f"http://127.0.0.1:{server.server_address[1]}"
  server.shutdown()


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path)


# TC-44 (offline parts): fetch + HTML-to-text + chunking + view_content_chunk + EC-25
def test_tc44_fetch_chunk_and_view(fixture_server, context):
  result = execute_read_url_content({"Url": f"{fixture_server}/page.html"}, context)
  assert "Heading" in result and "Paragraph one." in result
  assert "ignored()" not in result  # scripts stripped
  document_id = result.split("Document '")[1].split("'")[0]
  total = int(result.split("positions 1..")[1].split(" ")[0].rstrip("."))
  assert total >= 3
  second = execute_view_content_chunk({"document_id": document_id, "position": 2}, context)
  assert second.startswith(f"[chunk 2 of {total}]")
  with pytest.raises(ToolError) as error: execute_view_content_chunk({"document_id": document_id, "position": total + 1}, context)
  assert f"1..{total}" in str(error.value)  # EC-25 names valid range
  with pytest.raises(ToolError): execute_view_content_chunk({"document_id": "doc_nope", "position": 1}, context)


def test_chunks_survive_new_context_via_disk(fixture_server, context, tmp_path):
  result = execute_read_url_content({"Url": f"{fixture_server}/plain.txt"}, context)
  document_id = result.split("Document '")[1].split("'")[0]
  fresh_context = ToolContext(workspace=tmp_path)  # simulates --resume
  assert "plain body" in execute_view_content_chunk({"document_id": document_id, "position": 1}, fresh_context)


# TC-45: 5 MB refusal + binary refusal (EC-18)
def test_tc45_size_and_binary_refusal(fixture_server, context):
  with pytest.raises(ToolError) as error: execute_read_url_content({"Url": f"{fixture_server}/huge.txt"}, context)
  assert "5 MB" in str(error.value)
  with pytest.raises(ToolError) as error: execute_read_url_content({"Url": f"{fixture_server}/binary.bin"}, context)
  assert "binary" in str(error.value)
  with pytest.raises(ToolError) as error: execute_read_url_content({"Url": f"{fixture_server}/image.png"}, context)
  assert "image/png" in str(error.value)


def test_network_error_names_url(context):
  with pytest.raises(ToolError) as error: execute_read_url_content({"Url": "http://127.0.0.1:1/unreachable"}, context)
  assert "127.0.0.1:1" in str(error.value)
  with pytest.raises(ToolError): execute_read_url_content({"Url": "ftp://example.com/x"}, context)


def test_html_to_text_and_chunking_units():
  assert html_to_text("<p>a</p><script>b()</script><p>c</p>") == "a\nc"
  chunks = chunk_text("A" * (CHUNK_CHARS * 2 + 10))
  assert len(chunks) == 3 and len(chunks[0]) == CHUNK_CHARS and len(chunks[2]) == 10


def test_render_search_results_format():
  results = [{"title": f"Title {index}", "url": f"https://example.com/{index}", "summary": "S" * 400} for index in range(7)]
  rendered = render_search_results(results)
  assert rendered.count("- Title") == 5  # capped at 5 results
  assert "S" * 300 in rendered and "S" * 301 not in rendered  # ~300-char summaries
  assert "read_url_content" in rendered  # trailing read-further prompt


def test_search_web_unavailable_without_support(context, workspace, clean_key_env, monkeypatch):
  from lana.config import load_lana_config
  from lana.providers import reset_adapter_cache
  from tests.scripted_adapter import write_script
  script = write_script(workspace / "s.jsonl", [{"text": "x"}])
  monkeypatch.setenv("LANA_SCRIPTED_ADAPTER", str(script))
  reset_adapter_cache()
  context.app_config = load_lana_config(workspace, require_keys=False)
  with pytest.raises(ToolError) as error: execute_search_web({"query": "anything"}, context)
  assert "EC-19" in str(error.value) or "no web search support" in str(error.value)
  reset_adapter_cache()


# TC-43: live search via websearch role (requires keys)
@pytest.mark.live
def test_tc43_search_web_live(tmp_path, monkeypatch):
  if not os.environ.get("OPENAI_API_KEY"): pytest.skip("OPENAI_API_KEY not set")
  from lana.config import load_lana_config
  from lana.providers import reset_adapter_cache
  from tests.conftest import write_config_dir
  monkeypatch.delenv("LANA_SCRIPTED_ADAPTER", raising=False)
  reset_adapter_cache()
  write_config_dir(tmp_path, key_lines=None)
  context = ToolContext(workspace=tmp_path, app_config=load_lana_config(tmp_path))
  result = execute_search_web({"query": "Python programming language official documentation"}, context)
  assert "read_url_content" in result and "https://" in result
  reset_adapter_cache()
