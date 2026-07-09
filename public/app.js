/* Тренажёр артиклей — логика, офлайн-first, синхронизация с Cloudflare D1 (аккаунты). */
(() => {
  "use strict";

  const API = "/api/progress";
  const LS_PROGRESS = "article-progress";
  const LS_TOKEN = "auth-token";   // JWT текущего пользователя
  const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const MASTER_RATIO = 0.95;   // доля выученных слов уровня, чтобы открыть следующий

  // --- состояние ---
  let WORDS = [];             // [{word, article, level, gloss?, ru?}]
  // { ключ: {correct, wrong, seen, m?} } + служебный ключ "__meta"
  // (m: 1 — слово выучено навсегда; __meta.unlockedIdx — достигнутый уровень)
  let progress = {};
  let current = null;         // текущее слово
  let lastKey = null;         // чтобы не повторять то же слово подряд
  let answered = false;       // на текущее слово уже ответили → ждём «дальше»
  let advTimer = null;
  let syncTimer = null;
  let lastPush = 0;           // время последней отправки на сервер (для троттлинга)
  let dirty = false;
  let syncState = "";         // текущее состояние синхронизации (для перерисовки подписи при смене языка)
  let accountEmail = null;    // email из /api/auth/me (для перерисовки при смене языка)
  let lastAnswerCorrect = null; // верным ли был последний ответ (для перерисовки подсказки)

  // ключ прогресса: гомографы (одно слово, разное значение) учитываются раздельно
  const keyOf = (w) => (w.gloss ? `${w.word} (${w.gloss})` : w.word);
  // перевод слова по языку интерфейса: русский — только при русском интерфейсе,
  // иначе (en и de) — английский; у гомографов это и есть их значение
  const trOf = (w) => (I18N.getLang() === "ru" ? (w.ru || w.en) : (w.en || w.ru)) || "";

  // --- DOM ---
  const $ = (id) => document.getElementById(id);
  const el = {
    level: $("level"), correct: $("stat-correct"), wrong: $("stat-wrong"),
    passed: $("stat-passed"), word: $("word"), gloss: $("gloss"),
    answers: $("answers"), hint: $("hint"), sync: $("sync"),
    overlay: $("overlay"), dataJson: $("data-json"), dataSummary: $("data-summary"),
    dialogMsg: $("dialog-msg"), accountInfo: $("account-info"),
    accountOverlay: $("account-overlay"), accountMsg: $("account-msg"),
    authOverlay: $("auth-overlay"), authTitle: $("auth-title"),
    btnSignin: $("btn-signin"), btnRegister: $("btn-register"), btnAccount: $("btn-account"),
    registerNudge: $("register-nudge"),
    progressFill: $("progress-fill"), progressLabel: $("progress-label"),
    statsBody: $("stats-body"), statsTable: $("stats-table"),
  };
  let statsSort = { col: "word", dir: 1 };   // колонка сортировки и направление (1 ↑, -1 ↓)
  const answerButtons = Array.from(document.querySelectorAll(".answer"));

  // ---------- хранилище ----------
  function loadLocal() {
    try {
      const raw = localStorage.getItem(LS_PROGRESS);
      const obj = raw ? JSON.parse(raw) : {};
      return obj && typeof obj === "object" && !Array.isArray(obj) ? obj : {};
    } catch { return {}; }
  }
  function saveLocal() {
    try { localStorage.setItem(LS_PROGRESS, JSON.stringify(progress)); } catch {}
  }
  function entryFor(w) {
    const k = keyOf(w);
    let s = progress[k];
    if (!s) { s = { correct: 0, wrong: 0, seen: 0 }; progress[k] = s; }
    return s;
  }

  // счётчики монотонно растут → безопасно объединять поэлементным максимумом
  function mergeMax(a, b) {
    const out = {};
    for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
      const x = a[key] || {}, y = b[key] || {};
      if (key === "__meta") {   // служебная запись: достигнутый уровень
        out[key] = { unlockedIdx: Math.max(x.unlockedIdx || 1, y.unlockedIdx || 1) };
        continue;
      }
      out[key] = {
        correct: Math.max(x.correct || 0, y.correct || 0),
        wrong: Math.max(x.wrong || 0, y.wrong || 0),
        seen: Math.max(x.seen || 0, y.seen || 0),
      };
      if ((x.m || 0) || (y.m || 0)) out[key].m = 1;   // «выучено» не отбирается
    }
    return out;
  }

  // разово помечаем выученные слова несгораемым флагом m — статус остаётся,
  // даже если потом отвечать неправильно (вес слова при этом растёт как обычно)
  function markMastered() {
    for (const [key, s] of Object.entries(progress)) {
      if (key.startsWith("__")) continue;
      if (!s.m && (s.correct || 0) >= 1 && (s.correct || 0) >= (s.wrong || 0)) s.m = 1;
    }
  }

  // ---------- сеть ----------
  const hasToken = () => !!localStorage.getItem(LS_TOKEN);
  function authHeaders() {
    const t = localStorage.getItem(LS_TOKEN);
    return t ? { Authorization: "Bearer " + t } : {};
  }
  // сессия истекла / токен невалиден → продолжаем анонимно (прогресс — локально)
  function dropAuth() {
    localStorage.removeItem(LS_TOKEN);
    clearTimeout(syncTimer);
    syncTimer = null;
    dirty = false;
    renderAuthUI();
  }
  async function apiGet() {
    const r = await fetch(API, { headers: authHeaders(), cache: "no-store" });
    if (r.status === 401) { dropAuth(); throw new Error("GET 401"); }
    if (!r.ok) throw new Error("GET " + r.status);
    return r.json();
  }
  async function apiPost(data) {
    const r = await fetch(API, {
      method: "POST",
      headers: { "content-type": "application/json", ...authHeaders() },
      body: JSON.stringify(data),
    });
    if (r.status === 401) { dropAuth(); throw new Error("POST 401"); }
    if (!r.ok) throw new Error("POST " + r.status);
    return r.json();
  }

  function setSync(state) {
    syncState = state || "";
    el.sync.className = "sync" + (state ? " " + state : "");
    const key = { ok: "syncOk", pending: "syncPending", offline: "syncOffline" }[state];
    el.sync.title = key ? I18N.t(key) : "";
  }
  // Синхронизация с D1 — троттлинг: источник правды localStorage (пишется
  // мгновенно), на сервер — не чаще раза в SYNC_INTERVAL, но гарантированно,
  // пока есть несохранённое. Хвост сессии уходит через flushSync при
  // сворачивании/закрытии страницы, поэтому длинный интервал безопасен.
  const SYNC_INTERVAL = 30_000;
  function scheduleSync() {
    if (!hasToken()) return;          // аноним: прогресс живёт только в localStorage
    dirty = true;
    setSync("pending");
    if (syncTimer !== null) return;   // отправка уже запланирована — едем с ней
    const delay = Math.max(0, SYNC_INTERVAL - (Date.now() - lastPush));
    syncTimer = setTimeout(pushSync, delay);
  }
  async function pushSync() {
    clearTimeout(syncTimer);
    syncTimer = null;
    if (!dirty || !hasToken()) return;
    lastPush = Date.now();
    try { await apiPost(progress); dirty = false; setSync("ok"); }
    catch { setSync("offline"); }
  }
  // уход со страницы (закрытие вкладки, сворачивание PWA, переключение
  // приложения) — дослать остаток немедленно; keepalive переживает выгрузку
  function flushSync() {
    if (!dirty || !hasToken()) return;
    clearTimeout(syncTimer);
    syncTimer = null;
    lastPush = Date.now();
    dirty = false;
    fetch(API, {
      method: "POST",
      headers: { "content-type": "application/json", ...authHeaders() },
      body: JSON.stringify(progress),
      keepalive: true,
    }).then((r) => { if (!r.ok) throw new Error(); setSync("ok"); })
      .catch(() => { dirty = true; setSync("offline"); });
  }
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flushSync();
    else refreshWords();
  });
  window.addEventListener("pagehide", flushSync);
  window.addEventListener("online", () => { if (dirty) pushSync(); });

  // ---------- автообновление словаря ----------
  // Словарь читается один раз при старте, а вкладка/PWA может жить неделями:
  // после деплоя она продолжала бы работать со старой копией. Поэтому при
  // возвращении в приложение перечитываем words.json (не чаще раза в 10 минут).
  const WORDS_REFRESH_INTERVAL = 10 * 60 * 1000;
  let wordsFetchedAt = Date.now();
  async function refreshWords() {
    if (!WORDS.length) return;                       // приложение ещё не запустилось
    if (Date.now() - wordsFetchedAt < WORDS_REFRESH_INTERVAL) return;
    let fresh;
    try {
      fresh = await fetch("words.json", { cache: "no-store" }).then((r) => r.json());
    } catch { return; }                              // нет сети — работаем со старой копией
    if (!Array.isArray(fresh) || !fresh.length) return;
    wordsFetchedAt = Date.now();
    WORDS = fresh;                                   // текущая карточка не трогается
    updateStats();                                   // уровни и прогресс могли сдвинуться
    const u = unlockedLevels();
    el.level.textContent = I18N.t("level", { level: u[u.length - 1] });
  }

  // ---------- прогресс по уровням ----------
  // выучено, если стоит несгораемый флаг m или счёт в пользу верных ответов
  function isMastered(w) {
    const s = progress[keyOf(w)];
    return !!s && (s.m === 1 || (s.correct >= 1 && s.correct >= s.wrong));
  }
  function levelMastered(level) {
    const lw = WORDS.filter((w) => w.level === level);
    if (!lw.length) return true;
    const m = lw.filter((w) => isMastered(w)).length;
    return m >= lw.length * MASTER_RATIO;
  }
  function unlockedLevels() {
    let count = 1; // A1 всегда открыт
    for (let i = 0; i < LEVELS.length - 1; i++) {
      if (levelMastered(LEVELS[i])) count = i + 2; else break;
    }
    // достигнутый уровень не отбирается — ни ошибками, ни пополнением словаря
    const saved = (progress.__meta && progress.__meta.unlockedIdx) || 1;
    if (count > saved) {
      progress.__meta = { unlockedIdx: count };
      saveLocal(); scheduleSync();
    }
    return LEVELS.slice(0, Math.min(Math.max(count, saved), LEVELS.length));
  }

  // ---------- выбор слова ----------
  function weightFor(w) {
    const s = progress[keyOf(w)] || { correct: 0, wrong: 0, seen: 0 };
    if (s.seen === 0) return 5;                       // новые слова — показываем охотно
    if (s.correct >= 3 && s.wrong === 0) return 0.1;  // хорошо выучено — редко
    let weight = 1 + s.wrong * 3 - s.correct * 0.5;   // где ошибался — чаще
    return Math.max(0.2, weight);
  }
  function pickWord() {
    const unlocked = unlockedLevels();
    const pool = WORDS.filter((w) => unlocked.includes(w.level));
    const list = pool.length > 1 ? pool.filter((w) => keyOf(w) !== lastKey) : pool;
    const src = list.length ? list : pool;
    let total = 0;
    for (const w of src) total += weightFor(w);
    let r = Math.random() * total;
    for (const w of src) { r -= weightFor(w); if (r <= 0) return w; }
    return src[src.length - 1];
  }

  // ---------- рендер ----------
  function updateStats() {
    let correct = 0, wrong = 0, passed = 0;
    for (const [key, s] of Object.entries(progress)) {
      if (key.startsWith("__")) continue;   // служебные записи — не статистика
      correct += s.correct || 0;
      wrong += s.wrong || 0;
      if ((s.seen || 0) > 0) passed++;
    }
    el.correct.textContent = correct;
    el.wrong.textContent = wrong;
    el.passed.textContent = passed;
    renderProgress();
  }

  // полоска прогресса до открытия следующего уровня
  function renderProgress() {
    if (!el.progressFill) return;
    const unlocked = unlockedLevels();
    const cur = unlocked[unlocked.length - 1];
    const idx = LEVELS.indexOf(cur);

    if (idx >= LEVELS.length - 1) {            // достигнут максимум — открыты все уровни
      el.progressFill.style.width = "100%";
      el.progressLabel.textContent = I18N.t("allLevelsUnlocked");
      return;
    }

    const lw = WORDS.filter((w) => w.level === cur);
    const needed = Math.ceil(lw.length * MASTER_RATIO);
    const mastered = lw.filter((w) => isMastered(w)).length;
    const pct = needed ? Math.min(100, Math.round((mastered / needed) * 100)) : 100;

    el.progressFill.style.width = pct + "%";
    el.progressLabel.textContent = I18N.t("toNextLevel", {
      level: LEVELS[idx + 1], m: Math.min(mastered, needed), n: needed, pct,
    });
  }
  function renderWord() {
    el.word.textContent = current.word;
    const unlocked = unlockedLevels();          // достигнутый уровень = самый высокий открытый
    el.level.textContent = I18N.t("level", { level: unlocked[unlocked.length - 1] });
    if (el.gloss) el.gloss.textContent = current.gloss ? "(" + trOf(current) + ")" : "";
    el.hint.textContent = "";
    el.hint.className = "hint";
    for (const b of answerButtons) {
      b.classList.remove("correct", "wrong");
      b.disabled = false;
    }
  }

  function correctLabel() {
    if (current.article === "Plural") return I18N.t("correctPlural", { word: current.word });
    const gl = current.gloss ? ` (${trOf(current)})` : "";   // значение гомографа — на языке интерфейса
    return I18N.t("correctArticle", { article: current.article, word: current.word, gloss: gl });
  }

  function answer(choice) {
    if (answered || !current) return;
    answered = true;
    const right = current.article;
    const s = entryFor(current);
    s.seen++;
    const isRight = choice === right;
    lastAnswerCorrect = isRight;
    if (isRight) s.correct++; else s.wrong++;
    if (s.correct >= 1 && s.correct >= s.wrong) s.m = 1;   // выучено — навсегда

    for (const b of answerButtons) {
      b.disabled = true;
      const a = b.dataset.article;
      if (a === right) b.classList.add("correct");
      else if (a === choice) b.classList.add("wrong");
    }
    if (isRight) {
      el.hint.textContent = I18N.t("correctExcl");
      el.hint.className = "hint correct";
    } else {
      el.hint.textContent = correctLabel();
      el.hint.className = "hint wrong";
    }
    // перевод показываем только после ответа (у гомографов значение видно и до)
    if (el.gloss && trOf(current)) el.gloss.textContent = "(" + trOf(current) + ")";

    lastKey = keyOf(current);
    saveLocal(); scheduleSync(); updateStats();

    clearTimeout(advTimer);
    advTimer = setTimeout(next, isRight ? 850 : 1700);
  }

  function next() {
    clearTimeout(advTimer);
    answered = false;
    current = pickWord();
    renderWord();
  }

  // ---------- ввод ----------
  answerButtons.forEach((b) => {
    b.addEventListener("click", (e) => {
      e.stopPropagation();                 // чтобы клик-ответ не пролистнул слово
      b.blur();                            // иначе Пробел/Enter «кликнут» кнопку снова
      if (!answered) answer(b.dataset.article);
    });
  });
  // после ответа — клик в области карточки листает дальше
  const dialogOpen = () => !el.overlay.hidden || !el.accountOverlay.hidden || !el.authOverlay.hidden;
  document.querySelector(".card").addEventListener("click", () => {
    if (answered && !dialogOpen()) next();
  });
  document.addEventListener("keydown", (e) => {
    if (dialogOpen()) return; // не мешаем при открытом окне
    // Пробел/Enter листают всегда: после ответа — дальше, до ответа — скип
    // без записи в статистику (слово ещё выпадет — вес не изменился)
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); next(); return; }
    if (answered) return;
    const map = { "1": "der", "2": "die", "3": "das", "4": "Plural" };
    if (map[e.key]) { e.preventDefault(); answer(map[e.key]); }
  });

  // ---------- диалог данных ----------
  // слов в статистике (без служебных записей вроде __meta)
  const statsCount = () => Object.keys(progress).filter((k) => !k.startsWith("__")).length;

  // таблица статистики с сортировкой по колонкам (алфавит — вторичный ключ)
  function renderStatsTable() {
    if (!el.statsBody) return;
    const rows = Object.entries(progress).filter(([word]) => !word.startsWith("__")).map(([word, s]) => ({
      word,
      correct: s.correct || 0,
      wrong: s.wrong || 0,
      seen: s.seen || 0,
    }));
    const { col, dir } = statsSort;
    const byWord = (a, b) => a.word.localeCompare(b.word, "de");
    rows.sort((a, b) => {
      if (col === "word") return byWord(a, b) * dir;
      const primary = (a[col] - b[col]) * dir;   // выбранная колонка — главный ключ
      return primary || byWord(a, b);             // при равенстве — по алфавиту (↑)
    });

    const frag = document.createDocumentFragment();
    for (const r of rows) {
      const tr = document.createElement("tr");
      const cells = [
        [r.word, ""], [r.correct, "num ok"], [r.wrong, "num bad"], [r.seen, "num"],
      ];
      for (const [val, cls] of cells) {
        const td = document.createElement("td");
        td.textContent = val;                     // textContent — без риска инъекции
        if (cls) td.className = cls;
        tr.appendChild(td);
      }
      frag.appendChild(tr);
    }
    el.statsBody.replaceChildren(frag);

    // индикатор направления на активном заголовке
    el.statsTable.querySelectorAll("th[data-col]").forEach((th) => {
      th.setAttribute(
        "aria-sort",
        th.dataset.col === col ? (dir === 1 ? "ascending" : "descending") : "none"
      );
    });
  }
  function setSort(col) {
    if (statsSort.col === col) statsSort.dir *= -1;       // тот же столбец — меняем направление
    else statsSort = { col, dir: col === "word" ? 1 : -1 }; // числа — сразу по убыванию (кто чаще — выше)
    renderStatsTable();
  }
  if (el.statsTable) {
    el.statsTable.querySelectorAll("th[data-col]").forEach((th) => {
      th.addEventListener("click", () => setSort(th.dataset.col));
    });
  }

  // окно «Статистика»
  function openData() {
    el.dataJson.value = JSON.stringify(progress, null, 2);
    el.dataSummary.textContent =
      I18N.t("dataSummary", { n: statsCount(), total: WORDS.length });
    el.dialogMsg.textContent = "";
    renderStatsTable();
    el.overlay.hidden = false;
  }
  function closeData() { el.overlay.hidden = true; }

  // окно «Аккаунт»
  function renderAccountInfo() {
    el.accountInfo.textContent = accountEmail ? I18N.t("signedInAs", { email: accountEmail }) : "—";
  }
  function openAccount() {
    el.accountMsg.textContent = "";
    el.accountInfo.textContent = "…";
    fetch("/api/auth/me", { headers: authHeaders(), cache: "no-store" })
      .then((r) => {
        if (r.status === 401) { closeAccount(); dropAuth(); return null; }  // токен протух → анонимный режим
        return r.ok ? r.json() : null;
      })
      .then((d) => { accountEmail = d && d.user ? d.user.email : null; renderAccountInfo(); })
      .catch(() => { accountEmail = null; renderAccountInfo(); });
    el.accountOverlay.hidden = false;
  }
  function closeAccount() { el.accountOverlay.hidden = true; }

  // ---------- вход / регистрация ----------
  // футер: аноним видит «Войти в аккаунт» и «Зарегистрироваться», вошедший — «Аккаунт» и точку синка
  function renderAuthUI() {
    const authed = hasToken();
    el.btnSignin.hidden = authed;
    el.btnRegister.hidden = authed;
    el.btnAccount.hidden = !authed;
    el.sync.hidden = !authed;
    el.registerNudge.hidden = authed;   // призыв под полоской прогресса — только анониму
  }
  let authForm = null;   // форма создаётся при первом открытии модалки
  const authTitleFor = (m) => I18N.t(m === "register" ? "registerSub" : "loginSub");
  function openAuth(mode) {
    // телефон (узкий экран) — отдельная страница, десктоп — модальное окно
    if (matchMedia("(max-width: 600px)").matches) {
      location.href = "/login.html" + (mode === "register" ? "?mode=register" : "");
      return;
    }
    if (!authForm) {
      authForm = AuthForm.mount($("auth-form"), {
        mode,
        showSub: false,                        // роль подзаголовка играет заголовок окна
        onSuccess: () => location.reload(),    // boot() сольёт локальный прогресс с серверным
        onModeChange: (m) => { el.authTitle.textContent = authTitleFor(m); },
      });
    } else {
      authForm.setMode(mode);                  // заодно чистит сообщение прошлой попытки
    }
    el.authOverlay.hidden = false;
    authForm.focus();
  }
  function closeAuth() { el.authOverlay.hidden = true; }

  $("btn-data").addEventListener("click", openData);
  $("btn-close").addEventListener("click", closeData);
  el.overlay.addEventListener("click", (e) => { if (e.target === el.overlay) closeData(); });
  $("btn-account").addEventListener("click", openAccount);
  $("btn-account-close").addEventListener("click", closeAccount);
  el.accountOverlay.addEventListener("click", (e) => { if (e.target === el.accountOverlay) closeAccount(); });
  el.btnSignin.addEventListener("click", () => openAuth("login"));
  el.btnRegister.addEventListener("click", () => openAuth("register"));
  $("btn-nudge-register").addEventListener("click", () => openAuth("register"));
  $("btn-auth-close").addEventListener("click", closeAuth);
  el.authOverlay.addEventListener("click", (e) => { if (e.target === el.authOverlay) closeAuth(); });

  $("btn-copy").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(el.dataJson.value); flash(I18N.t("copied")); }
    catch { el.dataJson.select(); flash(I18N.t("copyManual")); }
  });

  $("btn-import").addEventListener("click", () => {
    let obj;
    try { obj = JSON.parse(el.dataJson.value); }
    catch { flash(I18N.t("errInvalidJson"), true); return; }
    if (!obj || typeof obj !== "object" || Array.isArray(obj)) { flash(I18N.t("errExpectObject"), true); return; }
    progress = obj;
    markMastered();               // старые бэкапы без флагов m — помечаем
    saveLocal(); scheduleSync(); updateStats(); renderStatsTable();
    flash(I18N.t("imported"));
  });

  $("btn-reset").addEventListener("click", () => {
    if (!confirm(I18N.t("confirmReset"))) return;
    progress = {};
    lastKey = null;
    saveLocal(); scheduleSync(); updateStats(); renderStatsTable(); next();
  });

  $("btn-logout").addEventListener("click", async () => {
    if (!confirm(I18N.t("confirmLogout"))) return;
    try { await pushSync(); } catch {}          // сохраняем несинхронизированное перед выходом
    try { await fetch("/api/auth/logout", { method: "POST", headers: authHeaders() }); } catch {}
    localStorage.removeItem(LS_TOKEN);
    localStorage.removeItem(LS_PROGRESS);       // чтобы прогресс не «перетёк» к другому аккаунту
    location.reload();                          // остаёмся в приложении — анонимный режим с нуля
  });

  $("btn-delete-account").addEventListener("click", async () => {
    if (!confirm(I18N.t("confirmDelete1"))) return;
    if (!confirm(I18N.t("confirmDelete2"))) return;
    try {
      const r = await fetch("/api/auth/delete", { method: "POST", headers: authHeaders() });
      if (!r.ok && r.status !== 401) { accountFlash(I18N.t("errDeleteFailed"), true); return; }
    } catch { accountFlash(I18N.t("errNetwork"), true); return; }
    localStorage.removeItem(LS_TOKEN);
    localStorage.removeItem(LS_PROGRESS);
    location.reload();                          // аккаунта больше нет — продолжаем анонимно
  });

  function flash(msg, isError) {
    el.dialogMsg.textContent = msg;
    el.dialogMsg.style.color = isError ? "var(--red)" : "var(--green)";
  }
  function accountFlash(msg, isError) {
    el.accountMsg.textContent = msg;
    el.accountMsg.style.color = isError ? "var(--red)" : "var(--green)";
  }

  // ---------- язык ----------
  // Статические строки перерисовывает сам i18n (data-i18n). Здесь — динамические,
  // которые i18n не видит: уровень, полоска прогресса, статус синхронизации, открытые диалоги, подсказка.
  function refreshDynamicText() {
    if (current) {
      const u = unlockedLevels();
      el.level.textContent = I18N.t("level", { level: u[u.length - 1] });
    }
    if (WORDS.length) renderProgress();
    setSync(syncState);
    if (answered && current) {
      el.hint.textContent = lastAnswerCorrect ? I18N.t("correctExcl") : correctLabel();
    }
    // перевод текущего слова: после ответа — всегда, до ответа — только у гомографов
    if (current && el.gloss) {
      const tr = trOf(current);
      if (answered && tr) el.gloss.textContent = "(" + tr + ")";
      else el.gloss.textContent = current.gloss ? "(" + tr + ")" : "";
    }
    if (!el.overlay.hidden) {
      el.dataSummary.textContent =
        I18N.t("dataSummary", { n: statsCount(), total: WORDS.length });
    }
    if (!el.accountOverlay.hidden) renderAccountInfo();
    if (!el.authOverlay.hidden && authForm) el.authTitle.textContent = authTitleFor(authForm.getMode());
  }
  I18N.mountSwitcher($("lang-switch"));
  I18N.onChange(refreshDynamicText);

  // ---------- старт ----------
  async function boot() {
    renderAuthUI();                 // приложение доступно и без входа — прогресс локально
    try {
      WORDS = await fetch("words.json", { cache: "no-store" }).then((r) => r.json());
    } catch {
      el.word.textContent = I18N.t("errLoadDict");
      if (el.gloss) el.gloss.textContent = I18N.t("errLoadDictSub");
      setSync("offline");
      return;
    }
    if (!Array.isArray(WORDS) || !WORDS.length) {
      el.word.textContent = I18N.t("dictEmpty");
      setSync("offline");
      return;
    }
    progress = loadLocal();
    markMastered();             // прогресс до этой версии — выученному ставим флаг
    updateStats();
    next();                     // работаем сразу, офлайн-first

    if (!hasToken()) return;    // аноним: без сервера, прогресс только на устройстве

    // затем подтягиваем сервер и мержим (не теряя локальные ответы)
    try {
      const server = await apiGet();
      if (server && typeof server === "object" && !Array.isArray(server)) {
        const merged = mergeMax(progress, server);
        if (JSON.stringify(merged) !== JSON.stringify(progress)) {
          progress = merged;
          markMastered();       // серверная копия могла быть без флагов m
          saveLocal(); updateStats();
        }
        if (JSON.stringify(merged) !== JSON.stringify(server)) scheduleSync();
        else setSync("ok");
      } else {
        setSync("ok");
      }
    } catch {
      setSync("offline");
    }
  }

  // регистрация service worker (PWA / офлайн)
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("sw.js").catch(() => {});
    });
  }

  boot();
})();
