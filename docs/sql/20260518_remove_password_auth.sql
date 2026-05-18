-- Run once against existing Railway/PostgreSQL databases after deploying the
-- password-auth removal. New databases use infra/postgres/schema.sql, which no
-- longer creates this column.
ALTER TABLE users DROP COLUMN IF EXISTS hashed_password;
