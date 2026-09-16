"""Cost engine: pricing lookup, per-turn cost, per-role session totals (LANAAGNT-FR-09, IS-16).

Usage normalization contract: input_tokens INCLUDES cache-read tokens (adapters normalize);
cost = (input - cache_read) x input_rate + cache_read x cached_rate + output x output_rate, rates per 1M.
"""
from dataclasses import dataclass, field
from typing import Optional
from lana.config import AppConfig
from lana.models import Usage


@dataclass
class RoleCost:
  usage: Usage = field(default_factory=Usage)
  cost_usd: float = 0.0
  priced: bool = True  # False once any turn had no pricing entry (EC-24)
  turns: int = 0


class CostTracker:
  def __init__(self, app: AppConfig):
    self.app = app
    self.by_role: dict[str, RoleCost] = {}

  def rates(self, role_name: str) -> Optional[dict]:
    role = self.app.roles.get(role_name)
    if role is None: return None
    return self.app.pricing.get(role.provider, {}).get(role.model_id)

  # Per-turn cost in USD; None when the model is missing from the pricing file (EC-24)
  def turn_cost(self, role_name: str, usage: Usage) -> Optional[float]:
    rates = self.rates(role_name)
    if rates is None: return None
    plain_input = max(usage.input_tokens - usage.cache_read_tokens, 0)
    cost = plain_input * rates.get("input_per_1m", 0.0) / 1e6
    cost += usage.cache_read_tokens * rates.get("cached_per_1m", rates.get("input_per_1m", 0.0)) / 1e6
    cost += usage.cache_write_tokens * rates.get("cache_write_per_1m", 0.0) / 1e6
    cost += usage.output_tokens * rates.get("output_per_1m", 0.0) / 1e6
    return round(cost, 6)

  # Record a finished turn and return its cost (also usable as Agent cost_fn)
  def record(self, role_name: str, usage: Usage) -> Optional[float]:
    entry = self.by_role.setdefault(role_name, RoleCost())
    entry.usage = entry.usage.add(usage)
    entry.turns += 1
    cost = self.turn_cost(role_name, usage)
    if cost is None: entry.priced = False
    else: entry.cost_usd += cost
    return cost

  # Restore totals from a resumed session log (IG-06, BG-0002)
  def seed(self, resumed) -> None:
    for role_name, usage in resumed.usage_by_role.items():
      entry = self.by_role.setdefault(role_name, RoleCost())
      entry.usage = entry.usage.add(usage)
      entry.turns += resumed.turns_by_role.get(role_name, 0)
      entry.cost_usd += resumed.cost_by_role.get(role_name, 0.0)
      if role_name not in resumed.cost_by_role and resumed.turns_by_role.get(role_name): entry.priced = False

  def session_total(self) -> tuple[float, bool]:
    total, fully_priced = 0.0, True
    for entry in self.by_role.values():
      total += entry.cost_usd
      if not entry.priced: fully_priced = False
    return round(total, 6), fully_priced

  @staticmethod
  def format_cost(cost: Optional[float]) -> str:
    return "?" if cost is None else f"${cost:.4f}"

  # /cost summary: per-role totals + session sum (FR-09)
  def summary(self) -> str:
    if not self.by_role: return "No usage recorded in this session."
    lines = []
    for role_name in ("generator", "summarizer", "websearch"):
      entry = self.by_role.get(role_name)
      if entry is None: continue
      cost_text = f"${entry.cost_usd:.4f}" if entry.priced else f"${entry.cost_usd:.4f}+? (pricing incomplete)"
      lines.append(f"{role_name}: {entry.turns} turn" + ("s" if entry.turns != 1 else "") + f" | in={entry.usage.input_tokens} (cache {entry.usage.cache_read_tokens}) out={entry.usage.output_tokens} | {cost_text}")
    total, fully_priced = self.session_total()
    lines.append(f"session total: ${total:.4f}" + ("" if fully_priced else " (+ unpriced turns)"))
    return "\n".join(lines)
