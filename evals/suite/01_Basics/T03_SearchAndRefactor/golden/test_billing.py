"""Smoke test for billing."""
from billing import compute_invoice_total


def test_compute_invoice_total():
  assert compute_invoice_total([{"price": 10.0, "quantity": 2}]) == 20.0
