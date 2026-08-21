# Как деплоить Artikel Drill

Деплой **ручной**. `git push` сам по себе сайт **не** выкатывает
(автосборка Cloudflare на этом проекте падает). Живой сайт обновляется только
командой ниже.

## Одна команда

```
npm run deploy
```

Что она делает по шагам:

1. **`predeploy`** — запускает `python tools/stamp_sw.py`. Скрипт считает хеш
   содержимого файлов из массива `SHELL` в `public/sw.js` и вписывает его как имя
   кэша: `const CACHE = "artikel-<хеш>"`. Так кэш service worker'а сбрасывается
   автоматически ровно тогда, когда реально изменились файлы (включая
   `words.json`). **Версию кэша руками менять не нужно.**
2. **`deploy`** — `wrangler pages deploy` заливает папку `public` на Cloudflare
   Pages (проект `artikel-trainer`, домены artikel-trainer.pages.dev и
   artikeldrill.com).

## Правильный порядок

```
# 1. Проверить локально
npm run dev

# 2. Закоммитить изменения (ДО деплоя), чтобы штамп попал в коммит:
npm run stamp-sw            # обновит имя кэша в public/sw.js, если файлы менялись
git add -A
git commit -m "…"
git push                    # это только сохраняет в GitHub, НЕ деплой

# 3. Выкатить на сайт
npm run deploy              # predeploy повторно проштампует — если ничего не
                           # менялось, хеш тот же и sw.js не тронется
```

> Если пропустить шаг `npm run stamp-sw` и сразу сделать `npm run deploy`, то
> `predeploy` изменит `public/sw.js` уже после коммита — в рабочей копии появится
> небольшой diff. Тогда просто закоммить его: `git commit -am "stamp sw"` и
> `git push`. Ничего страшного, но чище — штамповать до коммита (шаг 2).

## Проверить, что выкатилось

Windows-консоль коверкает кириллицу — читать JSON с явным UTF-8:

```
curl -s "https://artikeldrill.com/words.json?cb=%RANDOM%" -o tmp.json
python -c "import json,io,sys; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8'); [print(e['ru']) for e in json.load(open('tmp.json',encoding='utf-8')) if e['word']=='НужноеСлово']"
```

Имя кэша в браузере: DevTools → Application → Cache Storage → должно быть
`artikel-<новый-хеш>` после деплоя.

## Прямой upload (если понадобится, в обход npm)

Пропускает штамп — тогда сначала `npm run stamp-sw`:

```
npm run stamp-sw
npx wrangler pages deploy public --project-name artikel-trainer --branch main --commit-dirty=true
```

## Коротко

- Деплой = **`npm run deploy`**. Больше ничего.
- `git push` ≠ деплой.
- Версию кэша `artikel-vNN` руками не трогаем — она теперь хеш и ставится сама.
