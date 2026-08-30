"""Billing helpers for the demo shop."""


def compute_invoice_total(items):
  return sum(item["price"] * item["quantity"] for item in items)


def apply_discount(total, percent):
  return total * (1 - percent / 100)
