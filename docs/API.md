# API Documentation

Base URL: `/api/v1`

## Internal access

- `GET /auth/me` returns the configured internal user.
- There are no signup, login, token, or password endpoints; access is controlled by the VPN/private network or upstream ingress.

## Locations and wishlists

- `GET /locations`, `POST /locations`
- `GET /wishlists`, `POST /wishlists`

## Tracking

- `GET /tracking/search?q=amul&provider=blinkit&location_id=1`
- `POST /tracking/items`
- `GET /tracking/items`
- `DELETE /tracking/items/{item_id}`
- `GET /tracking/items/{item_id}/history`

## Analytics

- `GET /analytics/availability`
- `GET /analytics/prices/{item_id}`
- `GET /analytics/notifications`

## Admin

- `GET /admin/stats`
- `POST /admin/jobs/{job_id}/pause`


## Debug Monitoring Mode

- `GET /debug/monitoring` returns last live provider response timestamp, endpoint, raw response excerpt, latency, location, request status, headers used, last detected inventory change, and failed request logs.
