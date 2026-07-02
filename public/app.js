/* Тренажёр артиклей — логика, офлайн-first, синхронизация с Cloudflare KV. */
(() => {
  "use strict";

  const API = "/api/progress";
  const LS_PROGRESS = "article-progress";
  const LS_TOKEN = "sync-token";
  const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const MASTER_RATIO = 0.95;   // доля выученных слов уровня, чтобы открыть следующий

  // --- состояние ---
  let WORDS = [];             // [{word, article, level, gloss?, ru?}]
  let progress = {};          // { ключ: {correct, wrong, seen} }
  let current = null;         // текущее слово
  let lastKey = null;         // чтобы не повторять то же слово подряд
  let answered = false;       // на текущее слово уже ответили → ждём «дальше»
  let advTimer = null;
  let syncTimer = null;
  let dirty = false;

  // ключ прогресса: гомографы (одно слово, разное значение) учитываются раздельно
  const keyOf = (w) => (w.gloss ? `${w.word} (${w.gloss})` : w.word);

  // --- DOM ---
  const $ = (id) => document.getElementById(id);
  const el = {
    level: $("level"), correct: $("stat-correct"), wrong: $("stat-wrong"),
    passed: $("stat-passed"), word: $("word"), gloss: $("gloss"),
    answers: $("answers"), hint: $("hint"), sync: $("sync"),
    overlay: $("overlay"), dataJson: $("data-json"), dataSummary: $("data-summary"),
    dialogMsg: $("dialog-msg"), syncToken: $("sync-token"),
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
      out[key] = {
        correct: Math.max(x.correct || 0, y.correct || 0),
        wrong: Math.max(x.wrong || 0, y.wrong || 0),
        seen: Math.max(x.seen || 0, y.seen || 0),
      };
    }
    return out;
  }

  // ---------- сеть ----------
  function authHeaders() {
    const t = localStorage.getItem(LS_TOKEN);
    return t ? { Authorization: "Bearer " + t } : {};
  }
  // сессия истекла / пароль сменили → уводим на страницу входа
  function toLogin() { location.replace("/login.html"); }
  async function apiGet() {
    const r = await fetch(API, { headers: authHeaders(), cache: "no-store" });
    if (r.status === 401) { toLogin(); throw new Error("GET 401"); }
    if (!r.ok) throw new Error("GET " + r.status);
    return r.json();
  }
  async function apiPost(data) {
    const r = await fetch(API, {
      method: "POST",
      headers: { "content-type": "application/json", ...authHeaders() },
      body: JSON.stringify(data),
    });
    if (r.status === 401) { toLogin(); throw new Error("POST 401"); }
    if (!r.ok) throw new Error("POST " + r.status);
    return r.json();
  }

  function setSync(state) {
    el.sync.className = "sync" + (state ? " " + state : "");
    el.sync.title = {
      ok: "Синхронизировано", pending: "Сохранение…",
      offline: "Офлайн — сохранено локально, отправлю позже",
    }[state] || "";
  }
  function scheduleSync() {
    dirty = true;
    setSync("pending");
    clearTimeout(syncTimer);
    syncTimer = setTimeout(pushSync, 1200);
  }
  async function pushSync() {
    if (!dirty) return;
    try { await apiPost(progress); dirty = false; setSync("ok"); }
    catch { setSync("offline"); }
  }
  window.addEventListener("online", () => { if (dirty) pushSync(); });

  // ---------- прогресс по уровням ----------
  function isMastered(w) {
    const s = progress[keyOf(w)];
    return !!s && s.correct >= 1 && s.correct >= s.wrong;
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
    return LEVELS.slice(0, count);
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
    for (const s of Object.values(progress)) {
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
      el.progressLabel.textContent = "Все уровни открыты 🎉";
      return;
    }

    const lw = WORDS.filter((w) => w.level === cur);
    const needed = Math.ceil(lw.length * MASTER_RATIO);
    const mastered = lw.filter((w) => isMastered(w)).length;
    const pct = needed ? Math.min(100, Math.round((mastered / needed) * 100)) : 100;

    el.progressFill.style.width = pct + "%";
    el.progressLabel.textContent =
      `До уровня ${LEVELS[idx + 1]}: ${Math.min(mastered, needed)} / ${needed} слов (${pct}%)`;
  }
  function renderWord() {
    el.word.textContent = current.word;
    const unlocked = unlockedLevels();          // достигнутый уровень = самый высокий открытый
    el.level.textContent = "Уровень: " + unlocked[unlocked.length - 1];
    if (el.gloss) el.gloss.textContent = current.gloss ? "(" + current.gloss + ")" : "";
    el.hint.textContent = "";
    el.hint.className = "hint";
    for (const b of answerButtons) {
      b.classList.remove("correct", "wrong");
      b.disabled = false;
    }
  }

  function correctLabel() {
    if (current.article === "Plural") return `Правильно: Plural — ${current.word}`;
    const gl = current.gloss ? ` (${current.gloss})` : "";
    return `Правильно: ${current.article} ${current.word}${gl}`;
  }

  function answer(choice) {
    if (answered || !current) return;
    answered = true;
    const right = current.article;
    const s = entryFor(current);
    s.seen++;
    const isRight = choice === right;
    if (isRight) s.correct++; else s.wrong++;

    for (const b of answerButtons) {
      b.disabled = true;
      const a = b.dataset.article;
      if (a === right) b.classList.add("correct");
      else if (a === choice) b.classList.add("wrong");
    }
    if (isRight) {
      el.hint.textContent = "Верно!";
      el.hint.className = "hint correct";
    } else {
      el.hint.textContent = correctLabel();
      el.hint.className = "hint wrong";
    }
    // перевод показываем только после ответа (у гомографов значение видно и до)
    if (el.gloss && current.ru) el.gloss.textContent = "(" + current.ru + ")";

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
      if (!answered) answer(b.dataset.article);
    });
  });
  // после ответа — клик в области карточки листает дальше
  document.querySelector(".card").addEventListener("click", () => {
    if (answered && el.overlay.hidden) next();
  });
  document.addEventListener("keydown", (e) => {
    if (!el.overlay.hidden) return; // не мешаем при открытом диалоге
    if (answered && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); next(); return; }
    if (answered) return;
    const map = { "1": "der", "2": "die", "3": "das", "4": "Plural" };
    if (map[e.key]) { e.preventDefault(); answer(map[e.key]); }
  });

  // ---------- диалог данных ----------
  // таблица статистики с сортировкой по колонкам (алфавит — вторичный ключ)
  function renderStatsTable() {
    if (!el.statsBody) return;
    const rows = Object.entries(progress).map(([word, s]) => ({
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
        [r.word, ""], [r.correct, "num"], [r.wrong, "num"], [r.seen, "num"],
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

  function openData() {
    el.dataJson.value = JSON.stringify(progress, null, 2);
    const words = Object.keys(progress).length;
    el.dataSummary.textContent = `${words} слов в статистике · всего в словаре: ${WORDS.length}`;
    el.dialogMsg.textContent = "";
    el.syncToken.value = localStorage.getItem(LS_TOKEN) || "";
    renderStatsTable();
    el.overlay.hidden = false;
  }
  function closeData() { el.overlay.hidden = true; }

  $("btn-data").addEventListener("click", openData);
  $("btn-close").addEventListener("click", closeData);
  el.overlay.addEventListener("click", (e) => { if (e.target === el.overlay) closeData(); });

  $("btn-copy").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(el.dataJson.value); flash("Скопировано"); }
    catch { el.dataJson.select(); flash("Выдели и скопируй вручную"); }
  });

  $("btn-import").addEventListener("click", () => {
    let obj;
    try { obj = JSON.parse(el.dataJson.value); }
    catch { flash("Ошибка: невалидный JSON", true); return; }
    if (!obj || typeof obj !== "object" || Array.isArray(obj)) { flash("Ожидается объект", true); return; }
    progress = obj;
    saveLocal(); scheduleSync(); updateStats(); renderStatsTable();
    flash("Импортировано");
  });

  $("btn-reset").addEventListener("click", () => {
    if (!confirm("Сбросить всю статистику? Это действие необратимо.")) return;
    progress = {};
    lastKey = null;
    saveLocal(); scheduleSync(); updateStats(); next();
  });

  $("btn-logout").addEventListener("click", async () => {
    if (!confirm("Выйти? Для доступа снова понадобится пароль.")) return;
    try { await pushSync(); } catch {}          // сохраняем несинхронизированное перед выходом
    try { await fetch("/api/logout", { method: "POST" }); } catch {}
    location.replace("/login.html");
  });

  $("btn-save-token").addEventListener("click", () => {
    const t = el.syncToken.value.trim();
    if (t) localStorage.setItem(LS_TOKEN, t); else localStorage.removeItem(LS_TOKEN);
    flash("Токен сохранён");
    if (dirty) pushSync();
  });

  function flash(msg, isError) {
    el.dialogMsg.textContent = msg;
    el.dialogMsg.style.color = isError ? "var(--red)" : "var(--green)";
  }

  // ---------- старт ----------
  async function boot() {
    try {
      WORDS = await fetch("words.json", { cache: "no-store" }).then((r) => r.json());
    } catch {
      el.word.textContent = "Не удалось загрузить словарь";
      if (el.gloss) el.gloss.textContent = "проверь, что сервер запущен, и обнови страницу";
      setSync("offline");
      return;
    }
    if (!Array.isArray(WORDS) || !WORDS.length) {
      el.word.textContent = "Словарь пуст";
      setSync("offline");
      return;
    }
    progress = loadLocal();
    updateStats();
    next();                     // работаем сразу, офлайн-first

    // затем подтягиваем сервер и мержим (не теряя локальные ответы)
    try {
      const server = await apiGet();
      if (server && typeof server === "object" && !Array.isArray(server)) {
        const merged = mergeMax(progress, server);
        if (JSON.stringify(merged) !== JSON.stringify(progress)) {
          progress = merged;
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
