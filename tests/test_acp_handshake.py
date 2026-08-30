"""ACP handshake, routing, and session creation tests (LANAACPB-IP01 Categories 2-3, TC-07..15)."""
import pytest
from lana.events import from_jsonl
from tests.acp_harness import AcpClient, assert_stdout_pure
from tests.conftest import write_config_dir, write_prompt_system


@pytest.fixture
def acp_workspace(tmp_path):
  workspace = tmp_path / "ws"
  workspace.mkdir()
  fake_system = write_prompt_system(tmp_path / "fake_system",
    rules={"alpha.md": "---\ntrigger: always_on\n---\nAlpha rule body"},
    workflows={"prime": "---\ndescription: Prime context\n---\n# Prime\n\nStep 1.", "verify": "---\ndescription: Verify work\n---\n# Verify\n\nStep 1."})
  write_config_dir(workspace, lana_overrides={"agent_folder": str(fake_system)})
  return workspace


@pytest.fixture
def client(acp_workspace):
  acp_client = AcpClient(acp_workspace).start()
  yield acp_client
  acp_client.stop()


# TC-07: initialize -> exact capability response per SPEC Data Structures (LANAACPB-IN01 shape)
def test_tc07_initialize_capabilities(client):
  result = client.handshake()
  assert result["protocolVersion"] == 1
  assert result["agentInfo"]["name"] == "lana" and result["agentInfo"]["version"]
  assert result["agentCapabilities"] == {"loadSession": True, "promptCapabilities": {"image": False, "audio": False, "embeddedContext": False}}


# TC-08: client requests protocolVersion 2 -> agent responds 1 (EC-04)
def test_tc08_version_negotiation(client):
  result = client.handshake(protocol_version=2)
  assert result["protocolVersion"] == 1


# TC-09: session method before initialize -> JSON-RPC error (EC-06)
def test_tc09_session_before_handshake(client):
  response, _ = client.request("session/new", {"cwd": str(client.workspace)})
  assert "error" in response and "handshake incomplete" in response["error"]["message"]


# TC-10: unknown method -> -32601; unparseable line -> -32700 with null id; connection alive after both (EC-01, EC-02)
def test_tc10_wire_errors_connection_survives(client):
  client.handshake()
  response, _ = client.request("session/definitely_not_a_method", {})
  assert response["error"]["code"] == -32601
  client.send_raw("{this is not json")
  parse_error = client.read_message()
  assert parse_error["error"]["code"] == -32700 and parse_error["id"] is None
  session_id, _ = client.session_new()  # connection still works
  assert session_id
  assert_stdout_pure(client)


# TC-11: second initialize -> error, previous handshake state kept (EC-07)
def test_tc11_second_initialize_rejected(client):
  client.handshake()
  response, _ = client.request("initialize", {"protocolVersion": 1})
  assert "error" in response and "already completed" in response["error"]["message"]
  session_id, _ = client.session_new()  # state survived
  assert session_id


# TC-12: session/new -> sessionId = JSONL file stem; first line is session_started (IG-02)
def test_tc12_session_new_creates_full_recall_jsonl(client):
  client.handshake()
  session_id, _ = client.session_new()
  session_file = client.workspace / ".lana-data" / "sessions" / f"{session_id}.jsonl"
  assert session_file.is_file()
  first_event = from_jsonl(session_file.read_text(encoding="utf-8").splitlines()[0])
  assert first_event.type == "session_started" and first_event.system_prompt


# TC-13: mcpServers + additionalDirectories -> ignored with stderr warnings, session still created (EC-19)
def test_tc13_ignored_params_warn(client):
  client.handshake()
  session_id, _ = client.session_new({"mcpServers": [{"name": "fs", "command": "npx", "args": [], "env": []}],
                                      "additionalDirectories": ["/other"]})
  assert session_id
  stderr = client.stderr_text()
  assert "'mcpServers' ignored" in stderr and "'additionalDirectories' ignored" in stderr


# TC-14: available_commands_update after session/new lists workflows, excludes built-ins
def test_tc14_available_commands(client):
  client.handshake()
  client.session_new()
  update = client.read_message()  # notification sent right after the response
  payload = update["params"]["update"]
  assert payload["sessionUpdate"] == "available_commands_update"
  names = [command["name"] for command in payload["availableCommands"]]
  assert names == ["prime", "verify"]
  assert not any(builtin in names for builtin in ("help", "cost", "exit"))


# TC-15: full stdout during handshake + session/new parses as JSON-RPC (IG-01)
def test_tc15_stdout_purity(client):
  client.handshake()
  client.session_new()
  client.read_message()  # drain available_commands_update
  client.close_stdin()
  assert client.wait_exit() == 0  # FR-01: EOF -> clean exit
  assert_stdout_pure(client)
  assert len(client.raw_stdout) >= 3  # initialize response, session/new response, commands update
