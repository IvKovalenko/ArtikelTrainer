Complete - Стадия 2 — прогресс per-user. Переписать functions/api/progress.js на чтение user_id из JWT и хранение в D1 (progress.data). Заменить старую одно-парольную защиту (\_middleware.js + SITE_PASSWORD) на настоящую auth.
Complete - Стадия 3 — фронтенд. Экраны регистрации/входа (ванильный JS), хранение токена, авто-логин через /me, кнопка выхода → уже есть каркас в login.html.
Стадия 4 — Capacitor. Обёртка проекта, сборка AAB, публикация в Play (без рекламы).
Стадия 5 — AdMob + UMP-consent.
Стадия 6 — юридическое: Privacy Policy, Data Safety, удаление аккаунта (in-app + web), сброс пароля по email (Resend).

Да — счётчики попыток лежат в таблице auth_attempts в D1. Просто очисти её в локальной базе одной командой (из корня проекта):

npx wrangler d1 execute artikel --local --command "DELETE FROM auth_attempts;"
После этого лимит сброшен, входи сразу.

Полезные варианты:

Сбросить только блокировку входа (оставить регистрацию):

npx wrangler d1 execute artikel --local --command "DELETE FROM auth_attempts WHERE key LIKE 'login:%';"
Посмотреть текущие счётчики:

npx wrangler d1 execute artikel --local --command "SELECT * FROM auth_attempts;"
Если случайно залочишься в проде — та же команда с --remote.
На будущее, если во время разработки лимит мешает — можно временно поднять пороги в functions/api/auth/login.js (сейчас 10, 15*60\*1000). Только верни обратно перед релизом. Хочешь, добавлю переменную окружения, чтобы отключать rate limit локально без правки кода?
