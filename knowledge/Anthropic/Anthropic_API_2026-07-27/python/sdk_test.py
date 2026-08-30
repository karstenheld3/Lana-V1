"""SDK integration test: verify parameter handling for each model method.
Uses real API calls with minimal tokens to document actual behavior.
Python SDK equivalent of javascript/sdk_test.cjs (22 tests).
"""
import json
import time
from pathlib import Path

import anthropic

# Load API key
keys_path = Path(__file__).resolve().parents[4] / ".api-keys.txt"
keys = {}
for line in keys_path.read_text(encoding="utf-8").splitlines():
  line = line.strip()
  if not line or line.startswith("#"):
    continue
  idx = line.index("=")
  keys[line[:idx].strip()] = line[idx + 1:].strip()

client = anthropic.Anthropic(api_key=keys["ANTHROPIC_API_KEY"])

PROMPT = [{"role": "user", "content": "Reply with exactly: OK"}]
results = []
test_num = 0

def test(label, create_fn):
  global test_num
  test_num += 1
  t0 = time.time()
  try:
    msg = create_fn()
    ms = int((time.time() - t0) * 1000)
    text_parts = []
    for b in msg.content:
      if b.type == "text":
        text_parts.append(b.text)
      elif b.type == "thinking":
        text_parts.append(f"[thinking: {b.thinking[:80]}...]")
      else:
        text_parts.append(f"[{b.type}]")
    text = " ".join(text_parts)
    r = {
      "n": test_num,
      "label": label,
      "status": "OK",
      "model": msg.model,
      "stop_reason": msg.stop_reason,
      "text": text[:200],
      "usage": {
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
      },
      "content_types": [b.type for b in msg.content],
      "ms": ms,
    }
    if hasattr(msg.usage, "output_tokens_details") and msg.usage.output_tokens_details:
      r["usage"]["thinking_tokens"] = getattr(msg.usage.output_tokens_details, "thinking_tokens", None)
    results.append(r)
    print(f"PASS  [{test_num}] {label} ({ms}ms) -> {text[:80]}")
  except Exception as err:
    ms = int((time.time() - t0) * 1000)
    status_code = getattr(err, "status_code", None)
    r = {
      "n": test_num,
      "label": label,
      "status": "FAIL",
      "error_type": type(err).__name__,
      "error_status": status_code,
      "error_message": str(err)[:300],
      "ms": ms,
    }
    results.append(r)
    print(f"FAIL  [{test_num}] {label} ({ms}ms) -> {status_code} {str(err)[:120]}")

def main():
  sdk_version = anthropic.__version__
  print(f"SDK version: {sdk_version}")
  print("=" * 80)

  # -- Sonnet 4.5: thinking method --
  test("sonnet-4.5 / thinking enabled budget=4000", lambda: client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=PROMPT,
  ))

  test("sonnet-4.5 / no thinking param", lambda: client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=PROMPT,
  ))

  test("sonnet-4.5 / thinking adaptive", lambda: client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  test("sonnet-4.5 / adaptive + effort=low", lambda: client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=PROMPT,
  ))

  # -- Opus 4.5: effort method --
  test("opus-4.5 / effort beta + output_config", lambda: client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=1024,
    output_config={"effort": "high"},
    messages=PROMPT,
    extra_headers={"anthropic-beta": "effort-2025-11-24"},
  ))

  test("opus-4.5 / effort NO beta header", lambda: client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=1024,
    output_config={"effort": "high"},
    messages=PROMPT,
  ))

  test("opus-4.5 / thinking adaptive", lambda: client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  test("opus-4.5 / thinking enabled budget=4000", lambda: client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=PROMPT,
  ))

  test("opus-4.5 / plain (no thinking, no effort)", lambda: client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=1024,
    messages=PROMPT,
  ))

  # -- Haiku 4.5: thinking method --
  test("haiku-4.5 / thinking enabled budget=4000", lambda: client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=PROMPT,
  ))

  test("haiku-4.5 / thinking adaptive", lambda: client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  test("haiku-4.5 / adaptive + effort=low", lambda: client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=PROMPT,
  ))

  # -- Opus 4.8: adaptive_thinking method --
  test("opus-4.8 / thinking adaptive", lambda: client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  test("opus-4.8 / adaptive + effort=high", lambda: client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=PROMPT,
  ))

  test("opus-4.8 / adaptive + effort=low", lambda: client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=PROMPT,
  ))

  test("opus-4.8 / thinking enabled budget=4000", lambda: client.messages.create(
    model="claude-opus-4-8",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=PROMPT,
  ))

  # -- Fable 5: adaptive_thinking method --
  test("fable-5 / thinking adaptive", lambda: client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  test("fable-5 / adaptive + effort=high", lambda: client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=PROMPT,
  ))

  test("fable-5 / adaptive + effort=low", lambda: client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=PROMPT,
  ))

  test("fable-5 / plain (no thinking)", lambda: client.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    messages=PROMPT,
  ))

  # -- Opus 4 (deprecated): thinking method --
  test("opus-4 / thinking enabled budget=4000", lambda: client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=PROMPT,
  ))

  test("opus-4 / thinking adaptive", lambda: client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=8192,
    thinking={"type": "adaptive"},
    messages=PROMPT,
  ))

  # -- Write results --
  print("\n" + "=" * 80)
  print("SUMMARY:")
  passed = sum(1 for r in results if r["status"] == "OK")
  failed = sum(1 for r in results if r["status"] == "FAIL")
  print(f"{passed} passed, {failed} failed out of {len(results)} tests")

  out_path = Path(__file__).parent / "sdk_test_results.json"
  out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
  print(f"Results written to {out_path}")

if __name__ == "__main__":
  main()
