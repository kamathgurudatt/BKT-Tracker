# Real Data Validation

This project now fails closed unless live provider endpoints are configured. It does not ship dummy inventory, static product lists, artificial stock states, or simulated restock notifications.

## Required live endpoint configuration

Set endpoint templates in `.env` using endpoints you are authorized to call and that are publicly accessible / observable from your own legitimate Blinkit app or web traffic:

```env
BLINKIT_SEARCH_URL_TEMPLATE=https://authorized.example/search?q={query}&lat={lat}&lon={lon}&pincode={pincode}
BLINKIT_PRODUCT_URL_TEMPLATE=https://authorized.example/product/{product_id}?lat={lat}&lon={lon}&pincode={pincode}
```

Supported placeholders are `{query}`, `{product_id}`, `{pincode}`, `{lat}`, and `{lon}`.

If these variables are empty, `/tracking/search` and worker polling return an explicit configuration error instead of fabricated data.

## Verification dashboard

The developer debug API is available at:

- `GET /api/v1/debug/monitoring`

It returns:

- last API response timestamp
- source endpoint called
- raw stock response excerpt
- response latency
- location queried
- success/failure state
- request headers used
- last detected inventory change
- recent failed requests

The Flutter app exposes the same data in **Debug Monitoring Mode** from the dashboard.

## Data quality gates before notification

Before a user alert is emitted, the worker:

1. Stores the live response as an inventory snapshot.
2. Computes an inventory-state hash and compares it to Redis cache state.
3. Runs event-based diff detection against the previous persisted snapshot.
4. Confirms in-stock transitions with a second live request.
5. Deduplicates alerts through Redis for `DUPLICATE_ALERT_WINDOW_SECONDS`.
6. Persists an `inventory_change_events` row for auditability.

## Screenshots

No screenshots of live Blinkit tracking are committed because that would require environment-specific authorized endpoint configuration and could expose private response payloads. After configuring live endpoints, run the app and capture the Dashboard → Debug Monitoring Mode flow locally.
