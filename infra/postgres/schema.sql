CREATE TYPE userrole AS ENUM ('USER', 'ADMIN');
CREATE TYPE stockstatus AS ENUM ('IN_STOCK', 'OUT_OF_STOCK', 'HIDDEN', 'UNKNOWN');
CREATE TYPE notificationtype AS ENUM ('RESTOCK', 'PRICE_DROP', 'STOCK_INCREASE', 'ETA_IMPROVED', 'SYSTEM');
CREATE TYPE jobstatus AS ENUM ('ACTIVE', 'PAUSED', 'FAILED');

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(320) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(120),
  role userrole NOT NULL DEFAULT 'USER',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  fcm_token TEXT,
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE locations (
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
CREATE INDEX ix_locations_user_enabled ON locations(user_id, enabled);
CREATE INDEX ix_locations_pincode ON locations(pincode);

CREATE TABLE wishlists (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_wishlists_user_id ON wishlists(user_id);

CREATE TABLE tracked_products (
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
CREATE INDEX ix_tracked_products_user_id ON tracked_products(user_id);
CREATE INDEX ix_tracked_products_category ON tracked_products(category);

CREATE TABLE inventory_snapshots (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  status stockstatus NOT NULL DEFAULT 'UNKNOWN',
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
CREATE INDEX ix_snapshots_product_location_time ON inventory_snapshots(tracked_product_id, location_id, observed_at DESC);
CREATE INDEX ix_snapshots_status ON inventory_snapshots(status);

CREATE TABLE price_history (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  price NUMERIC(10,2) NOT NULL,
  mrp NUMERIC(10,2),
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_price_history_product_location_time ON price_history(tracked_product_id, location_id, observed_at DESC);

CREATE TABLE notifications (
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
CREATE INDEX ix_notifications_user_id ON notifications(user_id);
CREATE INDEX ix_notifications_type ON notifications(type);

CREATE TABLE monitoring_jobs (
  id BIGSERIAL PRIMARY KEY,
  tracked_product_id BIGINT NOT NULL REFERENCES tracked_products(id) ON DELETE CASCADE,
  location_id BIGINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  status jobstatus NOT NULL DEFAULT 'ACTIVE',
  interval_seconds INTEGER NOT NULL DEFAULT 900,
  last_run_at TIMESTAMPTZ,
  next_run_at TIMESTAMPTZ,
  failure_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_monitoring_product_location UNIQUE (tracked_product_id, location_id)
);
CREATE INDEX ix_monitoring_jobs_due ON monitoring_jobs(status, next_run_at);
