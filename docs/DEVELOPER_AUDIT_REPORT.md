# Developer Audit Report (Live Inventory Integrity)

Date: 2026-05-13

## Blinkit endpoints used
- Search endpoint template: `BLINKIT_SEARCH_URL_TEMPLATE`
- Product endpoint template: `BLINKIT_PRODUCT_URL_TEMPLATE`

Both are mandatory for live operation. If not configured, provider calls fail closed with runtime errors and the API returns explicit unavailability instead of demo inventory.

## Polling intervals
- Default polling interval: `default_poll_interval_seconds` (default 900s)
- Minimum interval floor: `min_poll_interval_seconds` (default 300s)
- Test mode polling interval: fixed 15s for short-run verification

## Request headers
Provider requests are sent with:
- `User-Agent` (rotated from approved app values)
- `Accept: application/json,text/plain,*/*`

## Parser mappings
`normalize_product` and `normalize_search_results` parse real payload fields into:
- `external_product_id`
- `name`
- `price`
- `mrp`
- `discount_percent`
- `stock_status`
- `stock_quantity`
- `eta_minutes`
- `category`

## Sample real responses
Sample live payloads are exposed only at runtime through:
- `GET /api/v1/debug/monitoring` => `raw_stock_response`
- `POST /api/v1/debug/test-mode` => round-by-round payloads

No static sample payloads are embedded in source to avoid accidental fallback behavior.

## Stock transition examples
Transition evidence is persisted from real polling payloads in:
- `inventory_change_events.previous_payload`
- `inventory_change_events.latest_payload`
- `inventory_change_events.previous_hash`
- `inventory_change_events.latest_hash`

Notifications are only sent after diff detection and a second live confirmation poll for in-stock events.
