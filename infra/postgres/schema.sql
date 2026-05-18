-- BKT-Tracker / Blinkit Stock Sentinel schema
-- Enum values are lowercase to match SQLAlchemy Python enum definitions.

CREATE TYPE IF NOT EXISTS userrole AS ENUM ('user', 'admin');
CREATE TYPE IF NOT EXISTS stockstatus AS ENUM ('in_stock', 'out_of_stock', 'hidden', 'unknown');
CREATE TYPE IF NOT EXISTS notificationtype AS ENUM ('restock', 'price_drop', 'stock_increase', 'eta_improved', 'system');
CREATE TYPE IF NOT EXISTS jobstatus AS ENUM ('active', 'paused', 'failed');
CREATE TYPE IF NOT EXISTS requeststatus AS ENUM ('success', 'failure');

CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(320) NOT NULL UNIQUE,
  full_name VARCHAR(120),
  role userrole NOT NULL DEFAULT 'user',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  fcm_token TEXT,
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS locations (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  pincode VARCHAR(16),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_locations_user_enabled ON locations(user_id, enabled);
CREATE INDEX IF NOT EXISTS ix_locations_pincode ON locations(pincode);

CREATE TABLE IF NOT EXISTS wishlists (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_wishlists_user_id ON wishlists(user_id);

CREATE TABLE IF NOT EXISTS tracked_products (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  wishlist_id BIGINT REFERENCES wishlists(id) ON DELETE SET NULL,
  provider VARCHAR(40) NOT NULL DEFAULT 'blinkit',
  external_product_id VARCHAR(128) NOT NULL,
  name VARCHAR(255) NOT NULL,
  image_url TEXT,
  category VARCHAR(120),
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  target_price NUMERIC(10,2),
  alert_rules JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_user_provider_product UNIQUE (user_id, provider, external_product_id)
);
CREATE INDEX IF NOT EXISTS ix_tracked_products_user_id ON tracked_products(user_id);
CREATE INDEX IF NOT EXISTS ix_tracked_products_category ON tracked_products(category);

CREATE TABLE IF NOT EXISTS inventory_snapshots (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  status stockstatus NOT NULL DEFAULT 'unknown',
  price NUMERIC(10,2),
  mrp NUMERIC(10,2),
  discount_percent DOUBLE PRECISION,
  stock_quantity INTEGER,
  eta_minutes INTEGER,
  raw_payload JSONB NOT NULL DEFAULT '{}',
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_snapshots_product_location_time ON inventory_snapshots(tracked_product_id, location_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_snapshots_status ON inventory_snapshots(status);

CREATE TABLE IF NOT EXISTS price_history (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  price NUMERIC(10,2) NOT NULL,
  mrp NUMERIC(10,2),
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_price_history_product_location_time ON price_history(tracked_product_id, location_id, observed_at DESC);

CREATE TABLE IF NOT EXISTS notifications (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tracked_product_id BIGINT REFERENCES tracked_products(id) ON DELETE SET NULL,
  location_id BIGINT REFERENCES locations(id) ON DELETE SET NULL,
  type notificationtype NOT NULL,
  title VARCHAR(180) NOT NULL,
  body TEXT NOT NULL,
  channel VARCHAR(40) NOT NULL DEFAULT 'fcm',
  sent_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ,
  payload JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications(type);

CREATE TABLE IF NOT EXISTS monitoring_jobs (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  status jobstatus NOT NULL DEFAULT 'active',
  interval_seconds INTEGER NOT NULL DEFAULT 900,
  last_run_at TIMESTAMPTZ,
  next_run_at TIMESTAMPTZ,
  failure_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_monitoring_product_location UNIQUE (tracked_product_id, location_id)
);
CREATE INDEX IF NOT EXISTS ix_monitoring_jobs_due ON monitoring_jobs(status, next_run_at);

CREATE TABLE IF NOT EXISTS provider_request_logs (
  id BIGSERIAL PRIMARY KEY,
  provider VARCHAR(40) NOT NULL,
  endpoint TEXT NOT NULL,
  location_id BIGINT REFERENCES locations(id) ON DELETE SET NULL,
  tracked_product_id BIGINT REFERENCES tracked_products(id) ON DELETE SET NULL,
  status requeststatus NOT NULL,
  latency_ms INTEGER,
  request_headers JSONB NOT NULL DEFAULT '{}',
  response_excerpt JSONB NOT NULL DEFAULT '{}',
  error TEXT,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_provider_request_logs_provider ON provider_request_logs(provider);
CREATE INDEX IF NOT EXISTS ix_provider_logs_product_location_time ON provider_request_logs(tracked_product_id, location_id, fetched_at DESC);

CREATE TABLE IF NOT EXISTS inventory_change_events (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  change_type VARCHAR(60) NOT NULL,
  previous_hash VARCHAR(64),
  latest_hash VARCHAR(64) NOT NULL,
  previous_payload JSONB NOT NULL DEFAULT '{}',
  latest_payload JSONB NOT NULL DEFAULT '{}',
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_change_events_product_location_time ON inventory_change_events(tracked_product_id, location_id, detected_at DESC);
CREATE INDEX IF NOT EXISTS ix_inventory_change_events_change_type ON inventory_change_events(change_type);
