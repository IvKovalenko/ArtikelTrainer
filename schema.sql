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

-- Счётчики попыток для rate limiting (ключ = "<scope>:<ip>", напр. "login:1.2.3.4").
CREATE TABLE IF NOT EXISTS auth_attempts (
  key      TEXT PRIMARY KEY,
  count    INTEGER NOT NULL,
  reset_at INTEGER NOT NULL     -- unix ms, когда окно обнуляется
);

-- Одноразовые email-токены: сброс пароля и подтверждение адреса.
-- Хранится только SHA-256 от токена (сам токен — в ссылке письма).
CREATE TABLE IF NOT EXISTS email_tokens (
  token_hash TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose    TEXT NOT NULL,      -- 'reset' | 'verify'
  expires_at INTEGER NOT NULL    -- unix ms
);
