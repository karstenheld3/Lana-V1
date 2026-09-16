"""ACP JSON-RPC core unit tests (LANAACPB-IP01 Category 1, TC-01..06). No subprocess."""
import asyncio, json
import pytest
from lana.acp.jsonrpc import (
  PARSE_ERROR, ClientErrorResponse, Connection, Notification, ParseFailure, Request, Response,
  RoundTripCancelled, error_body, parse_line, to_line,
)


def make_connection(sent: list[str]) -> Connection:
  return Connection(read_line=None, write_line=sent.append)


# TC-01: parse request/notification/response fixtures -> correct message type and fields
def test_tc01_parse_message_types():
  request = parse_line('{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": 1}}')
  assert isinstance(request, Request) and request.id == 0 and request.method == "initialize" and request.params["protocolVersion"] == 1
  notification = parse_line('{"jsonrpc": "2.0", "method": "session/cancel", "params": {"sessionId": "s1"}}')
  assert isinstance(notification, Notification) and notification.method == "session/cancel"
  response = parse_line('{"jsonrpc": "2.0", "id": 100, "result": {"outcome": {"outcome": "selected", "optionId": "allow-once"}}}')
  assert isinstance(response, Response) and response.id == 100 and response.error is None
  error_response = parse_line('{"jsonrpc": "2.0", "id": 101, "error": {"code": -32800, "message": "Cancelled"}}')
  assert isinstance(error_response, Response) and error_response.error["code"] == -32800


# TC-02: malformed JSON -> parse-error sentinel (EC-01 input)
def test_tc02_malformed_lines():
  assert isinstance(parse_line("{not json"), ParseFailure)
  assert isinstance(parse_line('"just a string"'), ParseFailure)
  assert isinstance(parse_line('{"jsonrpc": "1.0", "method": "x"}'), ParseFailure)
  assert isinstance(parse_line('{"jsonrpc": "2.0", "id": 5}'), ParseFailure)  # neither method nor result/error


# TC-03: embedded newlines and CRLF -> single escaped line, round-trips (EC-05)
def test_tc03_newline_escaping():
  content = "line1\nline2\r\nline3"
  line = to_line({"method": "session/update", "params": {"update": {"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": content}}}})
  assert "\n" not in line and "\r" not in line
  parsed = json.loads(line)
  assert parsed["params"]["update"]["content"]["text"] == content and parsed["jsonrpc"] == "2.0"


# TC-04: agent-originated ids increment independently of client-originated ids
def test_tc04_id_spaces_independent():
  async def scenario():
    sent = []
    connection = make_connection(sent)
    task_one = asyncio.ensure_future(connection.request("session/request_permission", {}))
    task_two = asyncio.ensure_future(connection.request("elicitation/create", {}))
    await asyncio.sleep(0)
    first, second = json.loads(sent[0]), json.loads(sent[1])
    assert second["id"] == first["id"] + 1
    # a client-originated request with a colliding id must NOT touch the pending futures
    assert connection.resolve_response(Response(id="client-id-999", result={})) is False
    connection.resolve_response(Response(id=first["id"], result={"ok": 1}))
    connection.resolve_response(Response(id=second["id"], result={"ok": 2}))
    assert (await task_one) == {"ok": 1} and (await task_two) == {"ok": 2}
    assert connection.pending == {}
  asyncio.run(scenario())


# TC-05: response for unknown/settled id -> ignored with warning, no crash (EC-15)
def test_tc05_unknown_response_ignored(capsys):
  async def scenario():
    sent = []
    connection = make_connection(sent)
    lines = ['{"jsonrpc": "2.0", "id": 4711, "result": {}}']
    async def reader():
      return lines.pop(0) if lines else None
    connection.read_line = reader
    await connection.read_loop(dispatch=None)  # dispatch never reached for responses
  asyncio.run(scenario())
  assert "unknown request id 4711" in capsys.readouterr().err


# TC-06: cancel_pending resolves all outstanding futures as cancelled (IG-05 unit)
def test_tc06_cancel_pending():
  async def scenario():
    sent = []
    connection = make_connection(sent)
    task = asyncio.ensure_future(connection.request("session/request_permission", {}))
    await asyncio.sleep(0)
    connection.cancel_pending("session/cancel received")
    with pytest.raises(RoundTripCancelled):
      await task
    assert connection.pending == {}
  asyncio.run(scenario())


# Parse-error path through the read loop: -32700 with null id, connection continues (EC-01, TC-10 unit half)
def test_parse_error_response_then_continue():
  async def scenario():
    sent = []
    connection = make_connection(sent)
    lines = ["{garbage", '{"jsonrpc": "2.0", "method": "initialized", "params": {}}']
    dispatched = []
    async def reader():
      return lines.pop(0) if lines else None
    async def dispatch(message):
      dispatched.append(message)
    connection.read_line = reader
    await connection.read_loop(dispatch)
    error = json.loads(sent[0])
    assert error["id"] is None and error["error"]["code"] == PARSE_ERROR
    assert len(dispatched) == 1 and dispatched[0].method == "initialized"
  asyncio.run(scenario())


# Client error response -> ClientErrorResponse exception on the awaiting side (EC-14 unit half)
def test_client_error_response_raises():
  async def scenario():
    sent = []
    connection = make_connection(sent)
    task = asyncio.ensure_future(connection.request("session/request_permission", {}))
    await asyncio.sleep(0)
    request_id = json.loads(sent[0])["id"]
    connection.resolve_response(Response(id=request_id, error=error_body(-32603, "client exploded")))
    with pytest.raises(ClientErrorResponse):
      await task
  asyncio.run(scenario())
