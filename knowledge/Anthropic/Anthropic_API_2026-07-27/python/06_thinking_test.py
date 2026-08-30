"""IN15, IN51: Extended thinking, adaptive thinking, effort control."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import client, test, finish, DEFAULT_MODEL, OPUS_MODEL, ADAPTIVE_MODEL

def test_thinking_enabled():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 4000},
    messages=[{"role": "user", "content": "What is 15 * 37?"}],
  )
  types = [b.type for b in msg.content]
  thinking = next((b for b in msg.content if b.type == "thinking"), None)
  return {"content_types": types, "has_thinking": thinking is not None, "thinking_preview": thinking.thinking[:80] if thinking else None}

test("thinking: enabled (Sonnet 4.5)", test_thinking_enabled)

def test_thinking_adaptive():
  msg = client.messages.create(
    model=ADAPTIVE_MODEL, max_tokens=4096,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"content_types": [b.type for b in msg.content], "model": msg.model}

test("thinking: adaptive (Opus 4.8)", test_thinking_adaptive)

def test_adaptive_effort_high():
  msg = client.messages.create(
    model=ADAPTIVE_MODEL, max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "What is 15 * 37?"}],
  )
  return {"content_types": [b.type for b in msg.content]}

test("adaptive + effort=high (Opus 4.8)", test_adaptive_effort_high)

def test_adaptive_effort_low():
  msg = client.messages.create(
    model=ADAPTIVE_MODEL, max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": "Reply with: OK"}],
  )
  return {"content_types": [b.type for b in msg.content]}

test("adaptive + effort=low (Opus 4.8)", test_adaptive_effort_low)

# IN51: Effort without thinking (Opus 4.5)
def test_effort_only_opus45():
  msg = client.messages.create(
    model=OPUS_MODEL, max_tokens=64,
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Reply: OK"}],
  )
  return {"text": msg.content[0].text, "content_types": [b.type for b in msg.content]}

test("effort-only (Opus 4.5, no thinking param)", test_effort_only_opus45)

# IN15: Pass thinking blocks back in multi-turn
def test_multi_turn_thinking():
  r1 = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[{"role": "user", "content": "Reply with: FIRST"}],
  )
  r2 = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[
      {"role": "user", "content": "Reply with: FIRST"},
      {"role": "assistant", "content": r1.content},
      {"role": "user", "content": "Reply with: SECOND"},
    ],
  )
  text2 = next((b.text for b in r2.content if b.type == "text"), None)
  return {"turn1_types": [b.type for b in r1.content], "turn2_text": text2}

test("Multi-turn with thinking blocks", test_multi_turn_thinking)

finish(__file__)
