"""TK-026: cost engine (IP01 TC-48..49, FR-09)."""
from lana.config import load_lana_config
from lana.cost import CostTracker
from lana.models import Usage


def make_tracker(workspace):
  return CostTracker(load_lana_config(workspace, require_keys=False))


# TC-48: per-turn cost math matches hand-computed value to 4 decimals
def test_tc48_per_turn_cost_math(workspace):
  tracker = make_tracker(workspace)
  usage = Usage(input_tokens=21050, output_tokens=412, cache_read_tokens=18200)
  # generator = claude-sonnet: (21050-18200)x3.00 + 18200x0.30 + 412x15.00, per 1M
  expected = round((2850 * 3.00 + 18200 * 0.30 + 412 * 15.00) / 1e6, 4)
  assert round(tracker.turn_cost("generator", usage), 4) == expected == 0.0202
  # summarizer = gpt-4.1-mini: (1000-200)x0.40 + 200x0.10 + 100x1.60, per 1M
  small = Usage(input_tokens=1000, output_tokens=100, cache_read_tokens=200)
  assert round(tracker.turn_cost("summarizer", small), 6) == round((800 * 0.40 + 200 * 0.10 + 100 * 1.60) / 1e6, 6)


def test_missing_pricing_returns_none(workspace):
  tracker = make_tracker(workspace)
  tracker.app.pricing["anthropic"].pop("claude-sonnet-4-5-20250929")
  usage = Usage(input_tokens=1000, output_tokens=100)
  assert tracker.turn_cost("generator", usage) is None  # EC-24
  assert tracker.record("generator", usage) is None
  assert tracker.by_role["generator"].priced is False
  assert CostTracker.format_cost(None) == "?"


# TC-49: per-role accumulation across 3 turns + 1 compaction -> /cost shows all roles and session sum
def test_tc49_per_role_accumulation(workspace):
  tracker = make_tracker(workspace)
  for _ in range(3): tracker.record("generator", Usage(input_tokens=10000, output_tokens=500, cache_read_tokens=8000))
  tracker.record("summarizer", Usage(input_tokens=50000, output_tokens=2000))
  tracker.record("websearch", Usage(input_tokens=2000, output_tokens=300))
  summary = tracker.summary()
  assert "generator: 3 turns" in summary and "summarizer: 1 turn " in summary and "websearch: 1 turn " in summary
  assert "in=30000 (cache 24000) out=1500" in summary
  total, fully_priced = tracker.session_total()
  per_generator_turn = tracker.turn_cost("generator", Usage(input_tokens=10000, output_tokens=500, cache_read_tokens=8000))
  per_summarizer = tracker.turn_cost("summarizer", Usage(input_tokens=50000, output_tokens=2000))
  per_websearch = tracker.turn_cost("websearch", Usage(input_tokens=2000, output_tokens=300))
  assert abs(total - (3 * per_generator_turn + per_summarizer + per_websearch)) < 1e-9
  assert fully_priced and f"session total: ${total:.4f}" in summary


def test_empty_summary(workspace):
  assert "No usage recorded" in make_tracker(workspace).summary()
