import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.invoice.formatter import format_currency

def test_format_usd():
    assert format_currency(1234.56, "USD") == "$1,234.56"

def test_format_eur():
    assert format_currency(99.0, "EUR") == "€99.00"

def test_format_gbp():
    assert format_currency(250000.0, "GBP") == "£250,000.00"
