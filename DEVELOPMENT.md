# Разработка

Техническая документация. Описание проекта и логики выбора слов — в [README.md](README.md).

## Что внутри

```
public/                 статика (то, что раздаётся)
  index.html            разметка главного экрана
  style.css             стили
  app.js                логика тренажёра + офлайн + синхронизация
  i18n.js               локализация интерфейса (de/en/ru) + переключатель языка
  words.json            словарь A1–C2 (~2400 слов, поля ru/en), генерируется скриптом
  login.html            вход / регистрация
  delete-account.html   удаление аккаунта через веб (требование Google Play)
  privacy.html          политика конфиденциальности (de/en/ru)
  manifest.webmanifest  манифест PWA
  sw.js                 service worker (офлайн-кэш, network-first)
  icons/                иконки приложения
functions/
  _middleware.js        CORS для /api/*
  _lib/auth.js          общая библиотека: PBKDF2-пароли, JWT, rate limit
  api/progress.js       GET/POST статистики пользователя (D1)
  api/auth/             register / login / logout / me / delete
tools/
  gen_words.py          генератор words.json (правь списки здесь)
  translations.py       русские переводы {немецкое слово: перевод}
  translations_en.py    английские переводы (ключи зеркалят translations.py)
  gen_icons.py          генератор PNG-иконок из дизайна
schema.sql              схема базы D1 (users, progress, auth_attempts)
wrangler.toml           конфиг Cloudflare (папка сборки + привязка D1)
```

Хранилище — **Cloudflare D1** (SQLite): аккаунты (email + PBKDF2-хэш пароля),
прогресс (JSON на пользователя), счётчики rate-limit. Аутентификация — свой JWT
(HS256, Web Crypto), токен в `localStorage` + HttpOnly-cookie.

## Запуск локально

```bash
npm install
npx wrangler d1 execute artikel --local --file=./schema.sql   # один раз: создать таблицы
npm run dev          # http://127.0.0.1:8788  (локальная D1 — данные не уходят в облако)
```

Секреты для локальной разработки лежат в `.dev.vars` (в git не попадает),
нужен как минимум `JWT_SECRET`.

## Деплой на Cloudflare Pages

Нужен аккаунт Cloudflare (бесплатного тарифа хватает).

### 1. Логин и создание базы

```bash
npx wrangler login
npx wrangler d1 create artikel
# скопируй выданный database_id в wrangler.toml ([[d1_databases]])
npx wrangler d1 execute artikel --remote --file=./schema.sql   # создать таблицы в проде
npx wrangler pages secret put JWT_SECRET                       # длинная случайная строка
```

### 2. Публикация

```bash
npm run deploy
# при первом запуске wrangler спросит имя проекта — можно оставить artikel-trainer
```

После деплоя получишь адрес вида `https://artikel-trainer.pages.dev`.

> Деплой с не-main ветки создаёт **preview**-окружение со своими секретами —
> для продакшена деплой с `main` (или `npx wrangler pages deploy --branch main`).

### Полезное

```bash
# сколько аккаунтов в проде
npx wrangler d1 execute artikel --remote --command "SELECT COUNT(*) FROM users;"
# сбросить rate-limit локально
npx wrangler d1 execute artikel --local --command "DELETE FROM auth_attempts;"
```

## Установка на телефон

Открой адрес `*.pages.dev` в браузере телефона:

- **Android/Chrome**: меню → «Добавить на главный экран» (или всплывёт предложение установить).
- **iPhone/Safari**: «Поделиться» → «На экран Домой».

Появится иконка, приложение откроется в полноэкранном режиме и будет работать офлайн.

## Редактирование словаря

Правь списки в [tools/gen_words.py](tools/gen_words.py) (слова сгруппированы по уровню и роду),
переводы — в `tools/translations.py` (ru) и `tools/translations_en.py` (en), затем:

```bash
npm run words        # пересоберёт public/words.json
```

Скрипт сам сообщит о дубликатах и словах без перевода. После изменения статики
подними версию кэша в `public/sw.js` (`const CACHE = "artikel-vNN"`).

Иконки при желании перегенерировать: `npm run icons` (нужен Python + Pillow).

## Если порт занят

Вычисти зомби-процессы одной командой в PowerShell:

```powershell
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match 'wrangler' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Get-Process workerd -ErrorAction SilentlyContinue | Stop-Process -Force
```
