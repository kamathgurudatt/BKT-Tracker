# ER Diagram

```mermaid
erDiagram
  users ||--o{ locations : owns
  users ||--o{ wishlists : owns
  users ||--o{ tracked_products : tracks
  wishlists ||--o{ tracked_products : groups
  tracked_products ||--o{ inventory_snapshots : records
  tracked_products ||--o{ price_history : records
  tracked_products ||--o{ monitoring_jobs : schedules
  locations ||--o{ inventory_snapshots : scopes
  locations ||--o{ price_history : scopes
  locations ||--o{ monitoring_jobs : scopes
  users ||--o{ notifications : receives
```

The canonical SQL schema is in `infra/postgres/schema.sql` and includes indexes for user lookups, product-location time-series history, due monitoring jobs, and notification filtering.
