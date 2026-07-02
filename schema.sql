-- Схема Cloudflare D1 для многопользовательской версии.
-- Применить локально:  npx wrangler d1 execute artikel --local --file=./schema.sql
-- Применить в проде:    npx wrangler d1 execute artikel --remote --file=./schema.sql

CREATE TABLE IF NOT EXISTS users (
  id            TEXT PRIMARY KEY,              -- UUID
  email         TEXT NOT NULL UNIQUE,          -- в нижнем регистре
  password_hash TEXT NOT NULL,                 -- формат: pbkdf2$<iter>$<saltB64>$<hashB64>
  created_at    INTEGER NOT NULL,              -- unix ms
  email_verified INTEGER NOT NULL DEFAULT 0
);

-- Прогресс — один JSON-блоб на пользователя: {"Haus":{"correct":..,"wrong":..,"seen":..}, ...}
CREATE TABLE IF NOT EXISTS progress (
  user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  data       TEXT NOT NULL DEFAULT '{}',
  updated_at INTEGER NOT NULL
);
