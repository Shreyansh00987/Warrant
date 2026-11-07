import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.invoice.calculator import calculate_subtotal, calculate_tax, generate_invoice_summary

def test_subtotal():
    items = [
        {"price": 10.0, "quantity": 2},
        {"price": 5.0, "quantity": 1},
    ]
    assert calculate_subtotal(items) == 25.0

def test_tax_standard():
    items = [
        {"price": 100.0, "quantity": 1},
    ]
    assert calculate_tax(items, tax_rate=0.20) == 20.0

def test_tax_exempt_item():
    items = [
        {"price": 100.0, "quantity": 1, "tax_exempt": True},
    ]
    assert calculate_tax(items, tax_rate=0.20) == 0.0

def test_mixed_taxable_and_exempt():
    items = [
        {"price": 100.0, "quantity": 1, "tax_exempt": True},
        {"price": 50.0, "quantity": 1, "tax_exempt": False},
    ]
    assert calculate_tax(items, tax_rate=0.20) == 10.0

def test_invoice_summary():
    items = [
        {"price": 100.0, "quantity": 1, "tax_exempt": True},
        {"price": 50.0, "quantity": 1, "tax_exempt": False},
    ]
    summary = generate_invoice_summary(items, tax_rate=0.20)
    assert summary["subtotal"] == 150.0
    assert summary["tax"] == 10.0
    assert summary["total"] == 160.0
