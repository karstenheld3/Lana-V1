"""IN32-35, IN43: Admin APIs - organizations, users, workspaces, usage, rate limits.
Requires ANTHROPIC_ADMIN_KEY in .api-keys.txt.
"""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import httpx
from _lib import test, finish, ADMIN_KEY

BASE = "https://api.anthropic.com/v1"
HEADERS = {
  "x-api-key": ADMIN_KEY or "",
  "anthropic-version": "2023-06-01",
  "content-type": "application/json",
}
SKIP_NO_KEY = None if ADMIN_KEY else "ANTHROPIC_ADMIN_KEY not configured"

# IN32: GET /v1/organizations/me
def test_get_organization():
  resp = httpx.get(f"{BASE}/organizations/me", headers=HEADERS)
  resp.raise_for_status()
  org = resp.json()
  return {"id": org["id"], "name": org["name"], "type": org.get("type")}

test("GET /v1/organizations/me", test_get_organization, skip=SKIP_NO_KEY)

# IN33: GET /v1/organizations/users
def test_list_users():
  resp = httpx.get(f"{BASE}/organizations/users", headers=HEADERS, params={"limit": 5})
  resp.raise_for_status()
  data = resp.json()
  return {"count": len(data.get("data", [])), "has_more": data.get("has_more")}

test("GET /v1/organizations/users", test_list_users, skip=SKIP_NO_KEY)

# IN34: GET /v1/organizations/workspaces
def test_list_workspaces():
  resp = httpx.get(f"{BASE}/organizations/workspaces", headers=HEADERS, params={"limit": 5})
  resp.raise_for_status()
  data = resp.json()
  return {"count": len(data.get("data", [])), "has_more": data.get("has_more")}

test("GET /v1/organizations/workspaces", test_list_workspaces, skip=SKIP_NO_KEY)

# IN34: GET /v1/organizations/api_keys
def test_list_api_keys_workspace():
  resp = httpx.get(f"{BASE}/organizations/api_keys", headers=HEADERS, params={"limit": 5})
  resp.raise_for_status()
  data = resp.json()
  return {"count": len(data.get("data", [])), "has_more": data.get("has_more")}

test("GET /v1/organizations/api_keys", test_list_api_keys_workspace, skip=SKIP_NO_KEY)

# IN34: GET /v1/organizations/workspaces/{id}/members (requires workspace ID)
def test_list_workspace_members():
  # First get a workspace ID
  resp = httpx.get(f"{BASE}/organizations/workspaces", headers=HEADERS, params={"limit": 1})
  resp.raise_for_status()
  ws = resp.json().get("data", [])
  if not ws:
    return {"skipped": "no workspaces found"}
  ws_id = ws[0]["id"]
  resp2 = httpx.get(f"{BASE}/organizations/workspaces/{ws_id}/members", headers=HEADERS, params={"limit": 5})
  resp2.raise_for_status()
  data = resp2.json()
  return {"workspace_id": ws_id, "count": len(data.get("data", [])), "has_more": data.get("has_more")}

test("GET /v1/organizations/workspaces/{id}/members", test_list_workspace_members, skip=SKIP_NO_KEY)

finish(__file__)
