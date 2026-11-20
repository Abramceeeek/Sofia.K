# Payments prototype (made-up data only)

**Nothing here takes money**, talks to a payment provider, or is part of the Brain or either app. It is the audit's
payment architecture (`decisions/payment-architecture.md`) written as a small program, so its rules are tested before
any provider is chosen: `orders.py` (one file, standard library only) and `test_orders.py` (24 tests).

```bash
python -m pytest prototype/payments -q
```

What it pins down: the server sets the price; asking twice is asking once; a payment notification is believed only if
it is signed, recent and new; a notification that names a different amount or currency is held for a person; paid is
not booked; states only move along allowed lines whatever order notifications arrive in; refunds never exceed what was
paid; and every step is written to a trail that shows tampering.

`MockProvider` signs its notifications the way Stripe documents (`t=…,v1=HMAC-SHA256("<t>.<body>")`), so the checking
code is the shape the real one will have. It is not Stripe's library and must not be used as one: the real integration
uses the provider's own library to check signatures.

It is not run by CI (the Brain's workflow watches `brain/` only).
