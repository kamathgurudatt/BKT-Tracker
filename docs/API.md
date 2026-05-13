# API Documentation

Base URL: `/api/v1`

## Auth

- `POST /auth/signup` creates a user.
- `POST /auth/login` returns a JWT bearer token.
- `GET /auth/me` returns current user profile.

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
