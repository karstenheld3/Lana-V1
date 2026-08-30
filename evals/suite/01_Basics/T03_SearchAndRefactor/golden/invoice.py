"""Invoice rendering."""
from billing import compute_invoice_total, apply_discount


def render_invoice(items, discount_percent):
  total = compute_invoice_total(items)
  final = apply_discount(total, discount_percent)
  return f"Total: {total:.2f} | After discount: {final:.2f}"
