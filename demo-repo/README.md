# Target Demo Service (`demo-repo/`)

A small financial billing service used to demonstrate Warrant's deterministic scope gatekeeper.

## Structure
- `src/invoice/calculator.py`: Tax calculation logic (modified in W-014 pass demo).
- `src/invoice/formatter.py`: Currency display formatting (planned in W-015).
- `src/payments/stripe_gateway.py`: Restricted payment processing module (drifted into by agent during W-015, triggering deterministic scope block!).

## Running Tests
```bash
python -m pytest demo-repo/tests/
```
