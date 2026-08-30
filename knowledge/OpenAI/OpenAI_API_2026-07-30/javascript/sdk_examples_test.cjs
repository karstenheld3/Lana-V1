/**
 * SDK Examples Test - Verifies TypeScript examples from INFO documentation
 * against the live OpenAI API.
 *
 * SDK version: openai 7.2.0
 * Topics covered: IN06, IN13, IN15, IN16, IN25, IN26, IN55
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
  console.log("OpenAI JS SDK Examples Test");
  console.log("SDK version: openai 7.2.0");
  console.log("==========================\n");

  // IN06: Responses API - Basic
  console.log("IN06: Responses API");
  await runTest("responses_create", "IN06", async () => {
    const response = await client.responses.create({
      model: "gpt-4o-mini",
      input: "Say hello in one word.",
    });
    if (!response.id) throw new Error("No response ID");
  });

  await runTest("responses_streaming", "IN06", async () => {
    const stream = await client.responses.create({
      model: "gpt-4o-mini",
      input: "Count to 3.",
      stream: true,
    });
    let events = 0;
    for await (const event of stream) {
      events++;
    }
    if (events === 0) throw new Error("No stream events received");
  });

  await runTest("responses_with_instructions", "IN06", async () => {
    const response = await client.responses.create({
      model: "gpt-4o-mini",
      instructions: "You are a helpful assistant.",
      input: "What is 2+2?",
    });
    if (!response.output_text) throw new Error("No output text");
  });

  // IN13: Function Calling
  console.log("\nIN13: Function Calling");
  await runTest("function_calling", "IN13", async () => {
    const response = await client.responses.create({
      model: "gpt-4o-mini",
      input: "What is the weather in London?",
      tools: [
        {
          type: "function",
          name: "get_weather",
          description: "Get current weather",
          parameters: {
            type: "object",
            properties: { location: { type: "string" } },
            required: ["location"],
          },
        },
      ],
    });
    const hasToolCall = response.output.some((item) => item.type === "function_call");
    if (!hasToolCall) throw new Error("Expected function_call in output");
  });

  // IN15: Structured Outputs
  console.log("\nIN15: Structured Outputs");
  await runTest("structured_json_schema", "IN15", async () => {
    const response = await client.responses.create({
      model: "gpt-4o-mini",
      input: "List 3 fruits as JSON",
      text: {
        format: {
          type: "json_schema",
          name: "fruits",
          schema: {
            type: "object",
            properties: { fruits: { type: "array", items: { type: "string" } } },
            required: ["fruits"],
            additionalProperties: false,
          },
          strict: true,
        },
      },
    });
    const parsed = JSON.parse(response.output_text);
    if (!parsed.fruits) throw new Error("Missing fruits key in response");
  });

  await runTest("structured_json_object", "IN15", async () => {
    const response = await client.responses.create({
      model: "gpt-4o-mini",
      input: "Return JSON with key 'answer' and value 42",
      text: { format: { type: "json_object" } },
    });
    const parsed = JSON.parse(response.output_text);
    if (!("answer" in parsed)) throw new Error("Missing answer key");
  });

  // IN16: Reasoning
  console.log("\nIN16: Reasoning");
  await runTest("reasoning_basic", "IN16", async () => {
    const response = await client.responses.create({
      model: "o4-mini",
      input: "What is the square root of 144?",
      reasoning: { effort: "low" },
    });
    if (!response.output_text) throw new Error("No output");
  });

  // IN25: Embeddings
  console.log("\nIN25: Embeddings");
  await runTest("embeddings_create", "IN25", async () => {
    const result = await client.embeddings.create({
      model: "text-embedding-3-small",
      input: "Hello world",
    });
    if (!result.data[0].embedding.length) throw new Error("Empty embedding");
  });

  await runTest("embeddings_dimensions", "IN25", async () => {
    const result = await client.embeddings.create({
      model: "text-embedding-3-small",
      input: "Hello world",
      dimensions: 256,
    });
    if (result.data[0].embedding.length !== 256)
      throw new Error(`Expected 256 dims, got ${result.data[0].embedding.length}`);
  });

  // IN26: Moderations
  console.log("\nIN26: Moderations");
  await runTest("moderations_safe", "IN26", async () => {
    const result = await client.moderations.create({
      model: "omni-moderation-latest",
      input: "I love puppies",
    });
    if (result.results[0].flagged) throw new Error("Unexpected flag on safe content");
  });

  // IN55: Chat Completions
  console.log("\nIN55: Chat Completions");
  await runTest("chat_completions_basic", "IN55", async () => {
    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are helpful." },
        { role: "user", content: "Say hi in one word." },
      ],
    });
    if (!completion.choices[0].message.content) throw new Error("No content");
  });

  await runTest("chat_completions_streaming", "IN55", async () => {
    const stream = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: "Count to 3." }],
      stream: true,
    });
    let chunks = 0;
    for await (const chunk of stream) {
      chunks++;
    }
    if (chunks === 0) throw new Error("No chunks received");
  });

  // Summary
  const passed = results.filter((r) => r.status === "passed").length;
  const failed = results.filter((r) => r.status === "failed").length;
  const skipped = results.filter((r) => r.status === "skipped").length;
  const total = results.length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration_ms, 0);

  console.log(`\n==========================`);
  console.log(`Results: ${passed} passed, ${failed} failed, ${skipped} skipped (${total} total, ${totalDuration}ms)`);

  // Save results
  const output = {
    sdk_version: "openai 7.2.0",
    run_date: new Date().toISOString(),
    summary: { total, passed, failed, skipped, total_duration_ms: totalDuration },
    tests: results,
  };
  fs.writeFileSync(
    path.join(__dirname, "sdk_examples_results.json"),
    JSON.stringify(output, null, 2)
  );
  console.log("Saved sdk_examples_results.json");
}

main().catch(console.error);
