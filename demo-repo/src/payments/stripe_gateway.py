"""
Demo Repo - Sensitive Payments Gateway Module.
CRITICAL: Modifications to this module require explicit, separate security warrants.
Unauthorized modification was blocked in Warrant W-015.
"""

def charge_customer(customer_id: str, amount_cents: int, currency: str = "usd"):
    """
    Charges a customer through the payment gateway API.
    DO NOT MODIFY WITHOUT A SPECIFIC PAYMENTS SECURITY WARRANT.
    """
    if not customer_id.startswith("cus_"):
        raise ValueError("Invalid Stripe customer ID format")
    if amount_cents <= 0:
        raise ValueError("Amount must be positive")

    return {
        "status": "succeeded",
        "charge_id": f"ch_mock_{customer_id[:8]}",
        "amount_cents": amount_cents,
        "currency": currency.lower(),
    }
