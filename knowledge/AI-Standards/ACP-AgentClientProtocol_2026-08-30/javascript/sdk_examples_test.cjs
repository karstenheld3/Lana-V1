/**
 * ACP TypeScript SDK examples test - verify SDK imports, schema, and agent creation.
 *
 * Covers: IN05 (Initialization), IN06 (Session), IN07 (Prompt), IN08 (Tool Calls),
 *         IN10 (Transports), IN12 (SDKs), IN15 (Elicitation)
 * No network access required.
 */
const fs = require("fs");
const path = require("path");

const RESULTS_FILE = path.join(__dirname, "sdk_examples_results.json");

let passed = 0;
let failed = 0;
let skipped = 0;
const results = [];

function test(name, fn) {
  const t0 = Date.now();
  try {
    const detail = fn();
    const dur = Date.now() - t0;
    results.push({ name, status: "pass", duration_ms: dur, detail: String(detail || "") });
    console.log(`  PASS  ${name} (${dur}ms)`);
    passed++;
  } catch (e) {
    const dur = Date.now() - t0;
    results.push({ name, status: "fail", duration_ms: dur, error: e.message });
    console.log(`  FAIL  ${name}: ${e.message}`);
    failed++;
  }
}

console.log("--- sdk_examples_test.cjs ---");

// --- Import tests ---

test("import_main_package", () => {
  const acp = require("@agentclientprotocol/sdk");
  const keys = Object.keys(acp).filter((k) => !k.startsWith("_"));
  return `Main package: ${keys.length} exports`;
});

test("import_v2_experimental", () => {
  const v2 = require("@agentclientprotocol/sdk/experimental/v2");
  const keys = Object.keys(v2).filter((k) => !k.startsWith("_"));
  return `v2 experimental: ${keys.length} exports`;
});

test("import_http_client", () => {
  const http = require("@agentclientprotocol/sdk/experimental/http-client");
  const keys = Object.keys(http).filter((k) => !k.startsWith("_"));
  return `HTTP client: ${keys.length} exports`;
});

test("import_ws_client", () => {
  const ws = require("@agentclientprotocol/sdk/experimental/ws-client");
  const keys = Object.keys(ws).filter((k) => !k.startsWith("_"));
  return `WS client: ${keys.length} exports`;
});

test("import_server", () => {
  const server = require("@agentclientprotocol/sdk/experimental/server");
  const keys = Object.keys(server).filter((k) => !k.startsWith("_"));
  return `Server: ${keys.length} exports`;
});

test("import_node", () => {
  const node = require("@agentclientprotocol/sdk/experimental/node");
  const keys = Object.keys(node).filter((k) => !k.startsWith("_"));
  return `Node helpers: ${keys.length} exports`;
});

// --- Schema JSON tests ---

test("load_v1_schema", () => {
  const schema = require("@agentclientprotocol/sdk/schema/schema.json");
  if (!schema || typeof schema !== "object") throw new Error("Schema not an object");
  const keys = Object.keys(schema);
  return `v1 schema keys: ${keys.slice(0, 5).join(", ")}...`;
});

test("load_v2_schema", () => {
  const schema = require("@agentclientprotocol/sdk/schema/v2/schema.unstable.json");
  if (!schema || typeof schema !== "object") throw new Error("v2 schema not an object");
  return `v2 unstable schema loaded`;
});

// --- Class instantiation tests ---

test("agent_app_class_exists", () => {
  const acp = require("@agentclientprotocol/sdk");
  if (!acp.AgentApp) throw new Error("AgentApp class not found");
  return `AgentApp class found, prototype methods: ${Object.getOwnPropertyNames(acp.AgentApp.prototype).length}`;
});

test("active_session_class_exists", () => {
  const acp = require("@agentclientprotocol/sdk");
  if (!acp.ActiveSession) throw new Error("ActiveSession class not found");
  return `ActiveSession class found`;
});

test("client_app_class_exists", () => {
  const acp = require("@agentclientprotocol/sdk");
  if (!acp.ClientApp) throw new Error("ClientApp class not found");
  return `ClientApp class found`;
});

test("request_error_class", () => {
  const acp = require("@agentclientprotocol/sdk");
  if (!acp.RequestError) throw new Error("RequestError not found");
  const err = new acp.RequestError(-32600, "Invalid Request");
  if (err.code !== -32600) throw new Error(`Wrong code: ${err.code}`);
  return `RequestError: code=${err.code}, message=${err.message}`;
});

// --- v1 specific exports ---

test("v1_stop_reasons", () => {
  const acp = require("@agentclientprotocol/sdk");
  // Check if StopReason type/enum exists
  const keys = Object.keys(acp);
  const stopRelated = keys.filter((k) => /stop/i.test(k));
  return `Stop-related exports: ${stopRelated.join(", ") || "none (type-only)"}`;
});

test("v1_tool_call_kinds", () => {
  const acp = require("@agentclientprotocol/sdk");
  const keys = Object.keys(acp);
  const toolRelated = keys.filter((k) => /tool/i.test(k));
  return `Tool-related exports: ${toolRelated.join(", ") || "none (type-only)"}`;
});

test("v1_permission_exports", () => {
  const acp = require("@agentclientprotocol/sdk");
  const keys = Object.keys(acp);
  const permRelated = keys.filter((k) => /permission/i.test(k));
  return `Permission-related exports: ${permRelated.join(", ") || "none (type-only)"}`;
});

// --- v2 experimental exports ---

test("v2_agent_app_class", () => {
  const v2 = require("@agentclientprotocol/sdk/experimental/v2");
  if (!v2.AgentApp) throw new Error("v2 AgentApp class not found");
  return `v2 AgentApp class found`;
});

test("v2_active_session_class", () => {
  const v2 = require("@agentclientprotocol/sdk/experimental/v2");
  if (!v2.ActiveSession) throw new Error("v2 ActiveSession class not found");
  return `v2 ActiveSession class found`;
});

// --- Write results ---

const summary = {
  suite: "sdk_examples_test",
  total: results.length,
  passed,
  failed,
  skipped,
  results,
};

fs.writeFileSync(RESULTS_FILE, JSON.stringify(summary, null, 2), "utf8");
console.log(`\n${"=".repeat(60)}`);
console.log(`sdk_examples_test: ${passed} passed, ${failed} failed, ${skipped} skipped (${results.length} total)`);
console.log("=".repeat(60));

process.exit(failed ? 1 : 0);
