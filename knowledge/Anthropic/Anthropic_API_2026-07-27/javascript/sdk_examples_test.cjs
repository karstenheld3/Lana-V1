// Test all TypeScript SDK examples from the documentation
// Each test mirrors a specific code example from IN05/IN06/IN07/IN13/IN21
const Anthropic = require("@anthropic-ai/sdk");
const fs = require("node:fs");
const path = require("node:path");

const keysPath = path.join(__dirname, "..", "..", ".api-keys.txt");
const keys = Object.fromEntries(
  fs.readFileSync(keysPath, "utf-8")
    .split("\n")
    .filter(l => l.trim() && !l.startsWith("#"))
    .map(l => { const i = l.indexOf("="); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const client = new Anthropic({ apiKey: keys.ANTHROPIC_API_KEY });

const results = [];
let testNum = 0;

async function test(label, fn) {
  testNum++;
  const t0 = Date.now();
  try {
    const info = await fn();
    const ms = Date.now() - t0;
    results.push({ n: testNum, label, status: "PASS", ms, ...info });
    console.log(`PASS  [${testNum}] ${label} (${ms}ms)`);
  } catch (err) {
    const ms = Date.now() - t0;
    results.push({ n: testNum, label, status: "FAIL", ms, error: err.message?.slice(0, 200) });
    console.log(`FAIL  [${testNum}] ${label} (${ms}ms) -> ${err.message?.slice(0, 120)}`);
  }
}

async function main() {
  console.log("Testing TypeScript SDK documentation examples...");
  console.log("=".repeat(80));

  // ── IN05 / IN06: Basic message ──
  await test("IN06: Basic message (non-streaming)", async () => {
    const message = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 128,
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
    });
    const text = message.content[0].type === "text" ? message.content[0].text : "";
    return { text, stop_reason: message.stop_reason, content_types: message.content.map(b => b.type) };
  });

  // ── IN06: With system prompt ──
  await test("IN06: With system prompt", async () => {
    const message = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 128,
      system: "You are a helpful assistant. Always reply with exactly: OK",
      messages: [{ role: "user", content: "Hello" }],
    });
    return { text: message.content[0].type === "text" ? message.content[0].text : "", stop_reason: message.stop_reason };
  });

  // ── IN06/IN07: Streaming with text_delta ──
  await test("IN07: Basic streaming (text_delta)", async () => {
    const stream = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 128,
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
      stream: true,
    });
    let text = "";
    const eventTypes = new Set();
    for await (const event of stream) {
      eventTypes.add(event.type);
      if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
        text += event.delta.text;
      }
    }
    return { text, event_types: [...eventTypes] };
  });

  // ── IN07: Full event handling (message_start, content_block_start, delta, stop, message_delta) ──
  await test("IN07: Full event handling (switch)", async () => {
    const stream = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 128,
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
      stream: true,
    });
    let model = "";
    let stopReason = "";
    let outputTokens = 0;
    let text = "";
    for await (const event of stream) {
      switch (event.type) {
        case "message_start": model = event.message.model; break;
        case "content_block_delta":
          if (event.delta.type === "text_delta") text += event.delta.text;
          break;
        case "message_delta":
          stopReason = event.delta.stop_reason;
          outputTokens = event.usage.output_tokens;
          break;
      }
    }
    return { model, text, stop_reason: stopReason, output_tokens: outputTokens };
  });

  // ── IN07/IN13: Streaming with thinking deltas ──
  await test("IN07/IN13: Streaming with thinking_delta", async () => {
    const stream = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
      stream: true,
    });
    let thinkingText = "";
    let answerText = "";
    const blockTypes = [];
    for await (const event of stream) {
      if (event.type === "content_block_start") {
        blockTypes.push(event.content_block.type);
      } else if (event.type === "content_block_delta") {
        if (event.delta.type === "thinking_delta") thinkingText += event.delta.thinking;
        else if (event.delta.type === "text_delta") answerText += event.delta.text;
      }
    }
    return { block_types: blockTypes, has_thinking: thinkingText.length > 0, answer: answerText };
  });

  // ── IN13: Manual thinking (non-streaming) ──
  await test("IN13: Manual thinking enabled (Sonnet 4.5)", async () => {
    const message = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 16000,
      thinking: { type: "enabled", budget_tokens: 4000 },
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
    });
    const types = message.content.map(b => b.type);
    const thinking = message.content.find(b => b.type === "thinking");
    const text = message.content.find(b => b.type === "text");
    return {
      content_types: types,
      has_thinking: !!thinking,
      thinking_preview: thinking ? thinking.thinking.slice(0, 80) : null,
      text: text ? text.text : null,
      thinking_tokens: message.usage.output_tokens_details?.thinking_tokens,
    };
  });

  // ── IN13: Adaptive thinking + effort (Opus 4.8) ──
  await test("IN13: Adaptive + effort=low (Opus 4.8)", async () => {
    const message = await client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 4096,
      thinking: { type: "adaptive" },
      output_config: { effort: "low" },
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
    });
    return {
      content_types: message.content.map(b => b.type),
      text: message.content.find(b => b.type === "text")?.text,
      thinking_tokens: message.usage.output_tokens_details?.thinking_tokens,
    };
  });

  // ── IN13: Effort-only (Opus 4.5) ──
  await test("IN13: Effort-only output_config (Opus 4.5)", async () => {
    const message = await client.messages.create({
      model: "claude-opus-4-5-20251101",
      max_tokens: 1024,
      output_config: { effort: "high" },
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
    });
    return {
      content_types: message.content.map(b => b.type),
      text: message.content.find(b => b.type === "text")?.text,
      has_thinking_block: message.content.some(b => b.type === "thinking"),
    };
  });

  // ── IN05: RequestOptions (signal, headers) ──
  await test("IN05: RequestOptions with signal + headers", async () => {
    const ac = new AbortController();
    const message = await client.messages.create(
      {
        model: "claude-sonnet-4-5-20250929",
        max_tokens: 128,
        messages: [{ role: "user", content: "Reply with exactly: OK" }],
      },
      {
        signal: ac.signal,
        headers: { "x-custom-test": "docs-verification" },
      }
    );
    return { text: message.content[0].type === "text" ? message.content[0].text : "", stop_reason: message.stop_reason };
  });

  // ── IN05: Error handling (BadRequestError) ──
  await test("IN05: Error handling (bad model -> error class)", async () => {
    try {
      await client.messages.create({
        model: "nonexistent-model-xyz",
        max_tokens: 128,
        messages: [{ role: "user", content: "Hello" }],
      });
      return { error: "Expected error but got success" };
    } catch (err) {
      const isApiError = err instanceof Anthropic.APIError;
      const className = err.constructor.name;
      return { caught: true, is_api_error: isApiError, class: className, status: err.status };
    }
  });

  // ── IN06: Prompt caching with cache_control on system ──
  await test("IN06: Prompt caching (cache_control on system)", async () => {
    const message = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 128,
      system: [
        {
          type: "text",
          text: "You are a helpful assistant. " + "x".repeat(2048),
          cache_control: { type: "ephemeral" },
        },
      ],
      messages: [{ role: "user", content: "Reply with exactly: OK" }],
    });
    return {
      text: message.content[0].type === "text" ? message.content[0].text : "",
      cache_creation: message.usage.cache_creation_input_tokens,
      cache_read: message.usage.cache_read_input_tokens,
    };
  });

  // ── IN06/IN21: Tool use with agentic loop ──
  await test("IN21: Tool use agentic loop", async () => {
    const tools = [
      {
        name: "get_weather",
        description: "Get current weather for a location.",
        input_schema: {
          type: "object",
          properties: { location: { type: "string", description: "City, State" } },
          required: ["location"],
        },
      },
    ];
    function getWeather(location) {
      return JSON.stringify({ temp: "72F", condition: "sunny", location });
    }

    const messages = [{ role: "user", content: "What's the weather in NYC?" }];
    let loops = 0;
    let finalText = "";

    for (let i = 0; i < 5; i++) {
      loops++;
      const response = await client.messages.create({
        model: "claude-sonnet-4-5-20250929",
        max_tokens: 1024,
        tools,
        messages,
      });

      if (response.stop_reason === "end_turn") {
        for (const block of response.content) {
          if (block.type === "text") finalText += block.text;
        }
        break;
      }

      messages.push({ role: "assistant", content: response.content });
      const toolResults = [];
      for (const block of response.content) {
        if (block.type === "tool_use") {
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: getWeather(block.input.location),
          });
        }
      }
      messages.push({ role: "user", content: toolResults });
    }
    return { loops, has_final_text: finalText.length > 0, text_preview: finalText.slice(0, 100) };
  });

  // ── IN21: Streaming tool use with input_json_delta ──
  await test("IN21: Streaming tool use (input_json_delta)", async () => {
    const tools = [
      {
        name: "get_weather",
        description: "Get current weather for a location.",
        input_schema: {
          type: "object",
          properties: { location: { type: "string", description: "City, State" } },
          required: ["location"],
        },
      },
    ];
    const stream = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 1024,
      tools,
      tool_choice: { type: "tool", name: "get_weather" },
      messages: [{ role: "user", content: "What's the weather in Tokyo?" }],
      stream: true,
    });

    let toolName = "";
    let toolInput = "";
    const deltaTypes = new Set();
    for await (const event of stream) {
      if (event.type === "content_block_start" && event.content_block.type === "tool_use") {
        toolName = event.content_block.name;
        toolInput = "";
      } else if (event.type === "content_block_delta") {
        deltaTypes.add(event.delta.type);
        if (event.delta.type === "input_json_delta") {
          toolInput += event.delta.partial_json;
        }
      }
    }
    const parsed = toolInput ? JSON.parse(toolInput) : null;
    return { tool_name: toolName, input_json: parsed, delta_types: [...deltaTypes] };
  });

  // ── IN13: Multi-turn with thinking blocks ──
  await test("IN13: Multi-turn (pass thinking blocks back)", async () => {
    const response1 = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 2000 },
      messages: [{ role: "user", content: "Reply with exactly: FIRST" }],
    });
    const hasThinking1 = response1.content.some(b => b.type === "thinking");

    const response2 = await client.messages.create({
      model: "claude-sonnet-4-5-20250929",
      max_tokens: 8192,
      thinking: { type: "enabled", budget_tokens: 2000 },
      messages: [
        { role: "user", content: "Reply with exactly: FIRST" },
        { role: "assistant", content: response1.content },
        { role: "user", content: "Reply with exactly: SECOND" },
      ],
    });
    const text2 = response2.content.find(b => b.type === "text")?.text;
    return { turn1_has_thinking: hasThinking1, turn2_text: text2, turn2_types: response2.content.map(b => b.type) };
  });

  console.log("=".repeat(80));
  const passed = results.filter(r => r.status === "PASS").length;
  const failed = results.filter(r => r.status === "FAIL").length;
  console.log(`SUMMARY: ${passed} passed, ${failed} failed out of ${results.length} tests`);

  fs.writeFileSync(
    path.join(__dirname, "sdk_examples_results.json"),
    JSON.stringify(results, null, 2)
  );
  console.log("Results written to sdk_examples_results.json");
}

main().catch(console.error);
