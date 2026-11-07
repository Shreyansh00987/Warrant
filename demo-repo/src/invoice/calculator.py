"""
Demo Repo - Invoice Calculation Module.
"""

def calculate_subtotal(items):
    return sum(item["price"] * item["quantity"] for item in items)


def calculate_tax(items, tax_rate=0.20):
    """
    Calculates tax across items, skipping tax-exempt items.
    Fixed in Warrant W-014.
    """
    total_tax = 0.0
    for item in items:
        if item.get("tax_exempt", False):
            continue
        total_tax += item["price"] * item["quantity"] * tax_rate
    return round(total_tax, 2)


def generate_invoice_summary(items, tax_rate=0.20):
    subtotal = calculate_subtotal(items)
    tax = calculate_tax(items, tax_rate)
    return {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": round(subtotal + tax, 2),
    }
