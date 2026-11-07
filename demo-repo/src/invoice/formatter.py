"""
Demo Repo - Invoice Formatter Module.
"""

def format_currency(amount, currency="USD"):
    """
    Formats amount according to ISO 4217 currency standards.
    """
    if currency.upper() == "USD":
        return f"${amount:,.2f}"
    elif currency.upper() == "EUR":
        return f"€{amount:,.2f}"
    elif currency.upper() == "GBP":
        return f"£{amount:,.2f}"
    return f"{amount:,.2f} {currency.upper()}"
