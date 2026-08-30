// SDK integration test: verify parameter handling for each model method
// Uses real API calls with minimal tokens to document actual behavior.
const Anthropic = require("@anthropic-ai/sdk");
const fs = require("node:fs");
const path = require("node:path");

// Load API key
const keysPath = path.join(__dirname, "..", "..", ".api-keys.txt");
const keys = Object.fromEntries(
  fs.readFileSync(keysPath, "utf-8")
    .split("\n")
    .filter(l => l.trim() && !l.startsWith("#"))
    .map(l => { const i = l.indexOf("="); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const client = new Anthropic({ apiKey: keys.ANTHROPIC_API_KEY });

const PROMPT = [{ role: "user", content: "Reply with exactly: OK" }];
const results = [];

async function test(label, createFn) {
  const t0 = Date.now();
  try {
    const msg = await createFn();
    const text = msg.content.map(b => {
      if (b.type === "text") return b.text;
      if (b.type === "thinking") return `[thinking: ${b.thinking.slice(0, 80)}...]`;
      return `[${b.type}]`;
    }).join(" ");
    const r = {
      label,
      status: "OK",
      model: msg.model,
      stop_reason: msg.stop_reason,
      text: text.slice(0, 200),
      usage: msg.usage,
      content_types: msg.content.map(b => b.type),
      ms: Date.now() - t0,
    };
    results.push(r);
    console.log(`PASS  ${label} (${r.ms}ms) -> ${text.slice(0, 80)}`);
  } catch (err) {
    const r = {
      label,
      status: "FAIL",
      error_type: err.constructor.name,
      error_status: err.status,
      error_message: err.message?.slice(0, 300),
      ms: Date.now() - t0,
    };
    results.push(r);
    console.log(`FAIL  ${label} (${r.ms}ms) -> ${err.status} ${err.message?.slice(0, 120)}`);
  }
}

async function main() {
  const sdkPkg = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "node_modules", "@anthropic-ai", "sdk", "package.json"), "utf-8"));
  console.log("SDK version:", sdkPkg.version);
  console.log("=".repeat(80));

  // ── Sonnet 4.5: thinking method ──────────────────────────────────────
  // Test 1: thinking enabled with budget
  await test("sonnet-4.5 / thinking enabled budget=4000", () =>
    client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: PROMPT,
    })
  );

  // Test 2: thinking disabled (no thinking param)
  await test("sonnet-4.5 / no thinking param", () =>
    client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 1024,
      messages: PROMPT,
    })
  );

  // Test 3: thinking adaptive (does sonnet 4.5 support it?)
  await test("sonnet-4.5 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  // Test 4: thinking adaptive + output_config effort
  await test("sonnet-4.5 / adaptive + effort=low", () =>
    client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      messages: PROMPT,
    })
  );

  // ── Opus 4.5: effort method ──────────────────────────────────────────
  // Test 5: effort beta header
  await test("opus-4.5 / effort beta + output_config", () =>
    client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 1024,
      output_config: { effort: "high" },
      messages: PROMPT,
    }, { headers: { "anthropic-beta": "effort-2025-11-24" } })
  );

  // Test 6: effort without beta header
  await test("opus-4.5 / effort NO beta header", () =>
    client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 1024,
      output_config: { effort: "high" },
      messages: PROMPT,
    })
  );

  // Test 7: adaptive thinking on opus 4.5 (should fail?)
  await test("opus-4.5 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  // Test 8: thinking enabled on opus 4.5
  await test("opus-4.5 / thinking enabled budget=4000", () =>
    client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: PROMPT,
    })
  );

  // Test 9: no special params on opus 4.5
  await test("opus-4.5 / plain (no thinking, no effort)", () =>
    client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 1024,
      messages: PROMPT,
    })
  );

  // ── Haiku 4.5: thinking method ───────────────────────────────────────
  await test("haiku-4.5 / thinking enabled budget=4000", () =>
    client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: PROMPT,
    })
  );

  await test("haiku-4.5 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  await test("haiku-4.5 / adaptive + effort=low", () =>
    client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      messages: PROMPT,
    })
  );

  // ── Opus 4.8: adaptive_thinking method ───────────────────────────────
  await test("opus-4.8 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  await test("opus-4.8 / adaptive + effort=high", () =>
    client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      output_config: { effort: "high" },
      messages: PROMPT,
    })
  );

  await test("opus-4.8 / adaptive + effort=low", () =>
    client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      messages: PROMPT,
    })
  );

  await test("opus-4.8 / thinking enabled budget=4000", () =>
    client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: PROMPT,
    })
  );

  // ── Fable 5: adaptive_thinking method ────────────────────────────────
  await test("fable-5 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-fable-5",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  await test("fable-5 / adaptive + effort=high", () =>
    client.messages.create({
      model: "claude-fable-5",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      output_config: { effort: "high" },
      messages: PROMPT,
    })
  );

  await test("fable-5 / adaptive + effort=low", () =>
    client.messages.create({
      model: "claude-fable-5",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      messages: PROMPT,
    })
  );

  await test("fable-5 / plain (no thinking)", () =>
    client.messages.create({
      model: "claude-fable-5",
      max_tokens: 1024,
      messages: PROMPT,
    })
  );

  // ── Opus 4 (deprecated but testable): thinking method ────────────────
  await test("opus-4 / thinking enabled budget=4000", () =>
    client.messages.create({
      model: "claude-opus-4-20250514",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: PROMPT,
    })
  );

  await test("opus-4 / thinking adaptive", () =>
    client.messages.create({
      model: "claude-opus-4-20250514",
      max_tokens: 8192,
      thinking: { type: "adaptive" },
      messages: PROMPT,
    })
  );

  // ── Write results ────────────────────────────────────────────────────
  console.log("\n" + "=".repeat(80));
  console.log("SUMMARY:");
  const passed = results.filter(r => r.status === "OK").length;
  const failed = results.filter(r => r.status === "FAIL").length;
  console.log(`${passed} passed, ${failed} failed out of ${results.length} tests`);

  const outPath = path.join(__dirname, "sdk_test_results.json");
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
  console.log(`Results written to ${outPath}`);
  process.exit(0);
}

main();
