/**
 * SDK Parameter Combination Test - Verifies model/parameter combinations
 * work correctly with the OpenAI JS SDK.
 *
 * SDK version: openai 7.2.0
 * Focus: Parameter validation, model compatibility, edge cases
 */

const fs = require("fs");
const path = require("path");
const OpenAI = require("openai");

// Load API key
const keysPath = path.resolve("e:/Dev/.tools/.api-keys.txt");
const keys = {};
fs.readFileSync(keysPath, "utf-8")
  .split("\n")
  .forEach((line) => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith("#") && trimmed.includes("=")) {
      const [k, ...v] = trimmed.split("=");
      keys[k.trim()] = v.join("=").trim();
    }
  });

const client = new OpenAI({
  apiKey: keys.OPENAI_API_KEY,
  organization: keys.OPENAI_ORGANIZATION || undefined,
});

const results = [];

async function runTest(name, topic, fn) {
  const start = Date.now();
  try {
    await fn();
    const duration = Date.now() - start;
    results.push({ name, topic, status: "passed", duration_ms: duration });
    console.log(`  PASS: ${name} (${duration}ms)`);
  } catch (err) {
    const duration = Date.now() - start;
    const error = err.message || String(err);
    results.push({ name, topic, status: "failed", duration_ms: duration, error });
    console.log(`  FAIL: ${name} - ${error.slice(0, 150)}`);
  }
}

function skip(name, topic, reason) {
  results.push({ name, topic, status: "skipped", duration_ms: 0, error: reason });
  console.log(`  SKIP: ${name} - ${reason}`);
}

async function main() {
  console.log("OpenAI JS SDK Parameter Tests");
  console.log("SDK version: openai 7.2.0");
  console.log("=============================\n");

  // Model compatibility tests
  console.log("Model Compatibility:");
  await runTest("gpt4o_mini_basic", "models", async () => {
    const r = await client.responses.create({ model: "gpt-4o-mini", input: "Hi" });
    if (!r.id) throw new Error("No response");
  });

  await runTest("o4_mini_reasoning", "models", async () => {
    const r = await client.responses.create({
      model: "o4-mini",
      input: "What is 2+2?",
      reasoning: { effort: "low" },
    });
    if (!r.output_text) throw new Error("No output");
  });

  // Parameter edge cases
  console.log("\nParameter Edge Cases:");
  await runTest("max_output_tokens", "params", async () => {
    const r = await client.responses.create({
      model: "gpt-4o-mini",
      input: "Write a haiku.",
      max_output_tokens: 50,
    });
    if (!r.output_text) throw new Error("No output");
  });

  await runTest("temperature_zero", "params", async () => {
    const r = await client.responses.create({
      model: "gpt-4o-mini",
      input: "What is 1+1?",
      temperature: 0,
    });
    if (!r.output_text) throw new Error("No output");
  });

  await runTest("store_false", "params", async () => {
    const r = await client.responses.create({
      model: "gpt-4o-mini",
      input: "Hello",
      store: false,
    });
    if (!r.id) throw new Error("No response ID");
  });

  // Web search tool
  console.log("\nTool Tests:");
  await runTest("web_search_preview", "tools", async () => {
    const r = await client.responses.create({
      model: "gpt-4o-mini",
      input: "What day is today?",
      tools: [{ type: "web_search_preview" }],
    });
    if (!r.output_text) throw new Error("No output");
  });

  // Models API
  console.log("\nModels API:");
  await runTest("models_list", "models_api", async () => {
    const models = await client.models.list();
    let count = 0;
    for await (const m of models) {
      count++;
      if (count > 5) break;
    }
    if (count === 0) throw new Error("No models returned");
  });

  await runTest("models_retrieve", "models_api", async () => {
    const model = await client.models.retrieve("gpt-4o-mini");
    if (model.id !== "gpt-4o-mini") throw new Error("Wrong model ID");
  });

  // Files API
  console.log("\nFiles API:");
  await runTest("files_list", "files_api", async () => {
    const files = await client.files.list();
    // Just verify the call works
    if (files === undefined) throw new Error("No response");
  });

  // Chat Completions compatibility
  console.log("\nChat Completions:");
  await runTest("chat_with_tools", "chat", async () => {
    const r = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: "What is 2+2?" }],
      tools: [
        {
          type: "function",
          function: {
            name: "calculate",
            description: "Calculate math",
            parameters: {
              type: "object",
              properties: { expression: { type: "string" } },
              required: ["expression"],
            },
          },
        },
      ],
    });
    if (!r.choices[0]) throw new Error("No choices");
  });

  await runTest("chat_json_mode", "chat", async () => {
    const r = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: "Return JSON: {\"x\": 1}" }],
      response_format: { type: "json_object" },
    });
    const parsed = JSON.parse(r.choices[0].message.content);
    if (typeof parsed !== "object") throw new Error("Not JSON");
  });

  // Audio
  console.log("\nAudio:");
  await runTest("tts_speech", "audio", async () => {
    const response = await client.audio.speech.create({
      model: "tts-1",
      voice: "alloy",
      input: "Hello test.",
    });
    const buffer = Buffer.from(await response.arrayBuffer());
    if (buffer.length < 100) throw new Error("Audio too short");
  });

  // Embeddings variants
  console.log("\nEmbeddings:");
  await runTest("embeddings_batch", "embeddings", async () => {
    const r = await client.embeddings.create({
      model: "text-embedding-3-small",
      input: ["Hello", "World"],
    });
    if (r.data.length !== 2) throw new Error("Expected 2 embeddings");
  });

  // Summary
  const passed = results.filter((r) => r.status === "passed").length;
  const failed = results.filter((r) => r.status === "failed").length;
  const skipped = results.filter((r) => r.status === "skipped").length;
  const total = results.length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration_ms, 0);

  console.log(`\n=============================`);
  console.log(
    `Results: ${passed} passed, ${failed} failed, ${skipped} skipped (${total} total, ${totalDuration}ms)`
  );

  // Save results
  const output = {
    sdk_version: "openai 7.2.0",
    run_date: new Date().toISOString(),
    summary: { total, passed, failed, skipped, total_duration_ms: totalDuration },
    tests: results,
  };
  fs.writeFileSync(
    path.join(__dirname, "sdk_test_results.json"),
    JSON.stringify(output, null, 2)
  );
  console.log("Saved sdk_test_results.json");
}

main().catch(console.error);
