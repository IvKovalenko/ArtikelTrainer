Complete - Стадия 2 — прогресс per-user. Переписать functions/api/progress.js на чтение user_id из JWT и хранение в D1 (progress.data). Заменить старую одно-парольную защиту (\_middleware.js + SITE_PASSWORD) на настоящую auth.
Complete - Стадия 3 — фронтенд. Экраны регистрации/входа (ванильный JS), хранение токена, авто-логин через /me, кнопка выхода → уже есть каркас в login.html.
Стадия 4 — Capacitor. Обёртка проекта, сборка AAB, публикация в Play (без рекламы).
Стадия 5 — AdMob + UMP-consent.
Complete - Стадия 6 — юридическое: Privacy Policy, Data Safety, удаление аккаунта (in-app + web)
not complete - сброс пароля по email (Resend).

Что нужно от тебя (по порядку)
Аккаунт на resend.com (бесплатный: 100 писем/день) → создай API Key.

npx wrangler pages secret put RESEND_API_KEY
npx wrangler d1 execute artikel --remote --file=./schema.sql # новая таблица email_tokens
npm run deploy

⚠️ Главный подводный камень: без своего домена Resend шлёт письма только на email владельца аккаунта Resend (с адреса onboarding@resend.dev). Для тестов самому себе — хватит. Для реальных пользователей нужен свой домен: Resend → Domains → добавить SPF/DKIM-записи в DNS, затем npx wrangler pages secret put MAIL_FROM со значением Artikeltrainer <noreply@твой-домен.de>. Домен можно купить прямо в Cloudflare (~$10/год) — заодно повесишь на него сайт вместо pages.dev.
Проверка после деплоя: зарегистрируйся на свой адрес (владельца Resend) → письмо → ссылка → вход; потом «Забыли пароль?» → письмо → смена пароля. Существующие аккаунты (твой) не заблокированы: email_verified у них уже стоит или вход по старому паролю просто продолжает работать после одного сброса — если что, могу выставить email_verified=1 всем существующим одной SQL-командой.

Как разблокировать регистрацию для остальных
Правильный путь — свой домен (~$10/год, можно купить в Cloudflare → Domain Registration): Resend → Domains → Add Domain → добавить выданные SPF/DKIM-записи в DNS → npx wrangler pages secret put MAIL_FROM со значением Artikeltrainer <noreply@твой-домен.de>. После этого письма пойдут на любые адреса.
Временный костыль для тестов: удалить секрет (npx wrangler pages secret delete RESEND_API_KEY) — тогда сработает dev-фолбэк, регистрация будет сразу подтверждённой без писем, как раньше. Вернёшь ключ — верификация снова включится.
