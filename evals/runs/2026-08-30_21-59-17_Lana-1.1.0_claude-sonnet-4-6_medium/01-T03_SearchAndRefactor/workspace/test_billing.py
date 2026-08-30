"""Smoke test for billing."""
from billing import calc_total


def test_calc_total():
  assert calc_total([{"price": 10.0, "quantity": 2}]) == 20.0
