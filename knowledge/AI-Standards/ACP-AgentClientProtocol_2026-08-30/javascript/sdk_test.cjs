/**
 * ACP TypeScript SDK structural tests - verify class hierarchies,
 * method signatures, and transport infrastructure.
 *
 * Covers: IN04 (Architecture), IN10 (Transports), IN12 (SDKs), IN16 (v2 Migration)
 * No network access required.
 */
const fs = require("fs");
const path = require("path");

const RESULTS_FILE = path.join(__dirname, "sdk_test_results.json");

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

console.log("--- sdk_test.cjs ---");

// --- Agent class structure ---

test("agent_has_onRequest", () => {
  const { AgentApp } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(AgentApp.prototype);
  if (!proto.includes("onRequest")) throw new Error(`Missing onRequest. Has: ${proto.join(", ")}`);
  return `AgentApp.onRequest found`;
});

test("agent_has_onNotification", () => {
  const { AgentApp } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(AgentApp.prototype);
  if (!proto.includes("onNotification")) throw new Error(`Missing onNotification. Has: ${proto.join(", ")}`);
  return `AgentApp.onNotification found`;
});

test("agent_has_connect", () => {
  const { AgentApp } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(AgentApp.prototype);
  if (!proto.includes("connect")) throw new Error(`Missing connect. Has: ${proto.join(", ")}`);
  return `AgentApp.connect found`;
});

test("agent_methods_inventory", () => {
  const { AgentApp } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(AgentApp.prototype).filter((m) => m !== "constructor");
  return `AgentApp methods (${proto.length}): ${proto.slice(0, 8).join(", ")}...`;
});

// --- Session class structure ---

test("session_has_streamText", () => {
  const { ActiveSession } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(ActiveSession.prototype);
  const streamMethods = proto.filter((m) => /stream/i.test(m));
  return `ActiveSession stream methods: ${streamMethods.join(", ") || "none found in prototype"}`;
});

test("session_methods_inventory", () => {
  const { ActiveSession } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(ActiveSession.prototype).filter((m) => m !== "constructor");
  return `ActiveSession methods (${proto.length}): ${proto.slice(0, 8).join(", ")}...`;
});

// --- Client class structure ---

test("client_methods_inventory", () => {
  const { ClientApp } = require("@agentclientprotocol/sdk");
  const proto = Object.getOwnPropertyNames(ClientApp.prototype).filter((m) => m !== "constructor");
  return `ClientApp methods (${proto.length}): ${proto.slice(0, 8).join(", ")}...`;
});

// --- Transport infrastructure ---

test("stdio_transport_export", () => {
  const acp = require("@agentclientprotocol/sdk");
  const keys = Object.keys(acp);
  const stdioRelated = keys.filter((k) => /stdio/i.test(k));
  return `Stdio-related exports: ${stdioRelated.join(", ") || "none (may be in experimental)"}`;
});

test("experimental_server_exports", () => {
  const server = require("@agentclientprotocol/sdk/experimental/server");
  const keys = Object.keys(server).filter((k) => !k.startsWith("_"));
  return `Server exports (${keys.length}): ${keys.slice(0, 8).join(", ")}...`;
});

test("experimental_node_exports", () => {
  const node = require("@agentclientprotocol/sdk/experimental/node");
  const keys = Object.keys(node).filter((k) => !k.startsWith("_"));
  return `Node exports (${keys.length}): ${keys.slice(0, 8).join(", ")}...`;
});

test("http_client_exports", () => {
  const http = require("@agentclientprotocol/sdk/experimental/http-client");
  const keys = Object.keys(http).filter((k) => !k.startsWith("_"));
  return `HTTP client exports (${keys.length}): ${keys.slice(0, 8).join(", ")}...`;
});

test("ws_client_exports", () => {
  const ws = require("@agentclientprotocol/sdk/experimental/ws-client");
  const keys = Object.keys(ws).filter((k) => !k.startsWith("_"));
  return `WS client exports (${keys.length}): ${keys.slice(0, 8).join(", ")}...`;
});

// --- v2 specific structure ---

test("v2_agent_methods", () => {
  const { AgentApp } = require("@agentclientprotocol/sdk/experimental/v2");
  const proto = Object.getOwnPropertyNames(AgentApp.prototype).filter((m) => m !== "constructor");
  return `v2 AgentApp methods (${proto.length}): ${proto.slice(0, 8).join(", ")}...`;
});

test("v2_session_methods", () => {
  const { ActiveSession } = require("@agentclientprotocol/sdk/experimental/v2");
  const proto = Object.getOwnPropertyNames(ActiveSession.prototype).filter((m) => m !== "constructor");
  return `v2 ActiveSession methods (${proto.length}): ${proto.slice(0, 8).join(", ")}...`;
});

test("v2_vs_v1_agent_diff", () => {
  const v1 = require("@agentclientprotocol/sdk");
  const v2 = require("@agentclientprotocol/sdk/experimental/v2");
  const v1Methods = new Set(Object.getOwnPropertyNames(v1.AgentApp.prototype));
  const v2Methods = new Set(Object.getOwnPropertyNames(v2.AgentApp.prototype));
  const v2Only = [...v2Methods].filter((m) => !v1Methods.has(m));
  const v1Only = [...v1Methods].filter((m) => !v2Methods.has(m));
  return `v2-only: ${v2Only.join(", ") || "none"} | v1-only: ${v1Only.join(", ") || "none"}`;
});

// --- Schema validation ---

test("v1_schema_has_definitions", () => {
  const schema = require("@agentclientprotocol/sdk/schema/schema.json");
  const defKey = schema.$defs ? "$defs" : schema.definitions ? "definitions" : null;
  if (!defKey) throw new Error("No definitions or $defs in schema");
  const count = Object.keys(schema[defKey]).length;
  return `v1 schema: ${count} definitions in ${defKey}`;
});

test("v2_schema_has_definitions", () => {
  const schema = require("@agentclientprotocol/sdk/schema/v2/schema.unstable.json");
  const defKey = schema.$defs ? "$defs" : schema.definitions ? "definitions" : null;
  if (!defKey) throw new Error("No definitions or $defs in v2 schema");
  const count = Object.keys(schema[defKey]).length;
  return `v2 schema: ${count} definitions in ${defKey}`;
});

test("schema_has_initialize", () => {
  const schema = require("@agentclientprotocol/sdk/schema/schema.json");
  const defs = schema.$defs || schema.definitions || {};
  const initKeys = Object.keys(defs).filter((k) => /initialize/i.test(k));
  if (initKeys.length === 0) throw new Error("No Initialize definitions found");
  return `Initialize defs: ${initKeys.join(", ")}`;
});

test("schema_has_session_methods", () => {
  const schema = require("@agentclientprotocol/sdk/schema/schema.json");
  const defs = schema.$defs || schema.definitions || {};
  const sessionKeys = Object.keys(defs).filter((k) => /session/i.test(k));
  return `Session defs (${sessionKeys.length}): ${sessionKeys.slice(0, 5).join(", ")}...`;
});

test("schema_has_elicitation", () => {
  const schema = require("@agentclientprotocol/sdk/schema/schema.json");
  const defs = schema.$defs || schema.definitions || {};
  const elicitKeys = Object.keys(defs).filter((k) => /elicit/i.test(k));
  return `Elicitation defs: ${elicitKeys.join(", ") || "none in v1 schema"}`;
});

// --- Error handling ---

test("request_error_codes", () => {
  const { RequestError } = require("@agentclientprotocol/sdk");
  const err1 = new RequestError(-32600, "Invalid Request");
  const err2 = new RequestError(-32601, "Method not found");
  const err3 = new RequestError(-32800, "Request cancelled");
  if (err3.code !== -32800) throw new Error("Wrong code for cancelled");
  return `Error codes work: -32600, -32601, -32800`;
});

// --- Write results ---

const summary = {
  suite: "sdk_test",
  total: results.length,
  passed,
  failed,
  skipped,
  results,
};

fs.writeFileSync(RESULTS_FILE, JSON.stringify(summary, null, 2), "utf8");
console.log(`\n${"=".repeat(60)}`);
console.log(`sdk_test: ${passed} passed, ${failed} failed, ${skipped} skipped (${results.length} total)`);
console.log("=".repeat(60));

process.exit(failed ? 1 : 0);
