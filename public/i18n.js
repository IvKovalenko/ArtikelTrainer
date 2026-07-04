/* Локализация интерфейса (de / en / ru).
   Лёгкий модуль без зависимостей: строки, переключатель языка, применение к DOM.
   Переводы слов словаря живут в words.json (поля ru/en) — их выбирает app.js
   по текущему языку: ru → русский, en и de → английский.

   Разметка:
     <element data-i18n="key">…</element>            → textContent
     <element data-i18n-title="key">                 → title
     <element data-i18n-placeholder="key">           → placeholder
     <element data-i18n-aria="key">                  → aria-label
   Динамические строки в JS: I18N.t(ключ, { параметр: значение }).
   Переключатель: I18N.mountSwitcher(container). */
(function (global) {
  "use strict";

  var LS_LANG = "lang";
  var SUPPORTED = ["de", "en", "ru"];   // порядок кнопок в переключателе
  var FALLBACK = "en";

  var STRINGS = {
    de: {
      language: "Sprache",
      // --- заголовки страниц ---
      docTitle: "Artikel Drill",
      docTitleLogin: "Anmelden — Artikel Drill",
      docTitleDelete: "Konto löschen — Artikel Drill",
      appTitle: "Artikel Drill",
      // --- главный экран ---
      level: "Niveau: {level}",
      wordsPassed: "Wörter geübt",
      progressTitle: "Fortschritt bis zum nächsten Niveau",
      allLevelsUnlocked: "Alle Niveaus freigeschaltet 🎉",
      toNextLevel: "Bis Niveau {level}: {m} / {n} Wörter ({pct}%)",
      correctExcl: "Richtig!",
      correctPlural: "Richtig: Plural — {word}",
      correctArticle: "Richtig: {article} {word}{gloss}",
      registerNudge: "Du willst deinen Fortschritt behalten und auf anderen Geräten weitermachen?",
      registerNudgeCta: "Registriere dich!",
      keySpace: "Leertaste",
      keyNext: "— weiter",
      // --- нижняя панель ---
      statistics: "Statistik",
      account: "Konto",
      signInLink: "Anmelden",
      registerLink: "Registrieren",
      syncOk: "Synchronisiert",
      syncPending: "Wird gespeichert…",
      syncOffline: "Offline — lokal gespeichert, wird später synchronisiert",
      // --- диалог статистики ---
      close: "Schließen",
      colWord: "Wort",
      colCorrectTitle: "Richtige Antworten",
      colWrongTitle: "Falsche Antworten",
      colSeen: "Gezeigt",
      colSeenTitle: "Wie oft gezeigt",
      jsonSummary: "Daten (JSON) — Export / Import",
      copy: "Kopieren",
      importFromField: "Aus Feld importieren",
      resetStats: "Statistik zurücksetzen",
      dataSummary: "{n} Wörter in der Statistik · gesamt im Wörterbuch: {total}",
      copied: "Kopiert",
      copyManual: "Markieren und manuell kopieren",
      errInvalidJson: "Fehler: ungültiges JSON",
      errExpectObject: "Ein Objekt wird erwartet",
      imported: "Importiert",
      confirmReset: "Die gesamte Statistik zurücksetzen? Das kann nicht rückgängig gemacht werden.",
      // --- диалог аккаунта ---
      logout: "Abmelden",
      privacyPolicy: "Datenschutzerklärung",
      deleteAccount: "Konto löschen",
      signedInAs: "Angemeldet als {email}",
      confirmLogout: "Abmelden? Zum erneuten Anmelden werden E-Mail und Passwort benötigt.",
      confirmDelete1: "Konto und alle Daten unwiderruflich löschen?",
      confirmDelete2: "Wirklich löschen? Das kann nicht rückgängig gemacht werden.",
      errDeleteFailed: "Konto konnte nicht gelöscht werden",
      // --- загрузка словаря ---
      errLoadDict: "Wörterbuch konnte nicht geladen werden",
      errLoadDictSub: "prüfe, ob der Server läuft, und lade die Seite neu",
      dictEmpty: "Wörterbuch ist leer",
      // --- вход / регистрация ---
      loginSub: "Bei deinem Konto anmelden",
      registerSub: "Registrieren",
      passwordPlaceholder: "Passwort",
      signIn: "Anmelden",
      createAccount: "Konto erstellen",
      toggleToRegister: "Kein Konto? Registrieren",
      toggleToLogin: "Schon ein Konto? Anmelden",
      errInvalidEmail: "Ungültige E-Mail",
      errWeakPassword: "Das Passwort muss mindestens 8 Zeichen lang sein",
      errEmailTaken: "Diese E-Mail ist bereits registriert",
      errInvalidCredentials: "Falsche E-Mail oder falsches Passwort",
      errMissingCredentials: "E-Mail und Passwort eingeben",
      errRateLimited: "Zu viele Versuche. Bitte kurz warten und erneut versuchen.",
      errRateLimitedFor: "Zu viele Versuche. Bitte in {min} Min. erneut versuchen.",
      errGeneric: "Fehler. Bitte erneut versuchen.",
      errNetwork: "Netzwerkfehler",
      // --- подтверждение email ---
      errNotVerified: "Bitte bestätige zuerst deine E-Mail — wir haben dir einen Link geschickt.",
      resendVerification: "Bestätigungs-E-Mail erneut senden",
      verifySent: "E-Mail gesendet. Prüfe deinen Posteingang (auch Spam).",
      registerCheckEmail: "Fast geschafft! Bestätige deine E-Mail über den Link im Postfach.",
      verifiedOk: "E-Mail bestätigt — du kannst dich jetzt anmelden.",
      errVerifyInvalid: "Der Bestätigungslink ist ungültig oder abgelaufen.",
      errMailFailed: "E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen.",
      // --- сброс пароля ---
      docTitleReset: "Passwort zurücksetzen — Artikel Drill",
      resetTitle: "Passwort zurücksetzen",
      forgotPassword: "Passwort vergessen?",
      resetRequestSub: "Gib deine E-Mail ein — wir senden dir einen Link zum Zurücksetzen.",
      sendResetLink: "Link senden",
      resetSent: "Wenn ein Konto existiert, wurde eine E-Mail gesendet. Prüfe auch den Spam-Ordner.",
      resetNewSub: "Gib ein neues Passwort ein (mindestens 8 Zeichen).",
      newPasswordPlaceholder: "Neues Passwort",
      changePassword: "Passwort ändern",
      resetDone: "Passwort geändert! Weiterleitung…",
      errResetInvalid: "Der Link ist ungültig oder abgelaufen. Fordere einen neuen an.",
      backToLogin: "Zurück zur Anmeldung",
      // --- удаление аккаунта ---
      deleteAccountTitle: "Konto löschen",
      deleteAccountSub: "Gib E-Mail und Passwort ein, um dein Konto und die gesamte Statistik dauerhaft zu löschen. Das kann nicht rückgängig gemacht werden.",
      deleteForever: "Konto dauerhaft löschen",
      backToApp: "Zurück zur App",
      confirmDeleteFull: "Konto und alle Daten wirklich löschen? Das kann nicht rückgängig gemacht werden.",
      accountDeleted: "Konto gelöscht.",
      errDeleteFailedLater: "Konto konnte nicht gelöscht werden. Bitte später erneut versuchen.",
    },

    en: {
      language: "Language",
      docTitle: "Artikel Drill",
      docTitleLogin: "Sign in — Artikel Drill",
      docTitleDelete: "Delete account — Artikel Drill",
      appTitle: "Artikel Drill",
      level: "Level: {level}",
      wordsPassed: "words practiced",
      progressTitle: "Progress to the next level",
      allLevelsUnlocked: "All levels unlocked 🎉",
      toNextLevel: "To level {level}: {m} / {n} words ({pct}%)",
      correctExcl: "Correct!",
      correctPlural: "Correct: Plural — {word}",
      correctArticle: "Correct: {article} {word}{gloss}",
      registerNudge: "Don't want to lose your progress — and want to continue on other devices?",
      registerNudgeCta: "Register!",
      keySpace: "Space",
      keyNext: "— next",
      statistics: "Statistics",
      account: "Account",
      signInLink: "Sign in",
      registerLink: "Register",
      syncOk: "Synced",
      syncPending: "Saving…",
      syncOffline: "Offline — saved locally, will sync later",
      close: "Close",
      colWord: "Word",
      colCorrectTitle: "Correct answers",
      colWrongTitle: "Wrong answers",
      colSeen: "Shown",
      colSeenTitle: "How many times shown",
      jsonSummary: "Data (JSON) — export / import",
      copy: "Copy",
      importFromField: "Import from field",
      resetStats: "Reset statistics",
      dataSummary: "{n} words in statistics · total in dictionary: {total}",
      copied: "Copied",
      copyManual: "Select and copy manually",
      errInvalidJson: "Error: invalid JSON",
      errExpectObject: "An object is expected",
      imported: "Imported",
      confirmReset: "Reset all statistics? This cannot be undone.",
      logout: "Log out",
      privacyPolicy: "Privacy Policy",
      deleteAccount: "Delete account",
      signedInAs: "Signed in as {email}",
      confirmLogout: "Log out? You'll need your email and password to sign in again.",
      confirmDelete1: "Delete your account and all data permanently?",
      confirmDelete2: "Delete for sure? This cannot be undone.",
      errDeleteFailed: "Couldn't delete the account",
      errLoadDict: "Couldn't load the dictionary",
      errLoadDictSub: "check that the server is running and refresh the page",
      dictEmpty: "Dictionary is empty",
      loginSub: "Sign in to your account",
      registerSub: "Register",
      passwordPlaceholder: "Password",
      signIn: "Sign in",
      createAccount: "Create account",
      toggleToRegister: "No account? Register",
      toggleToLogin: "Already have an account? Sign in",
      errInvalidEmail: "Invalid email",
      errWeakPassword: "Password must be at least 8 characters",
      errEmailTaken: "This email is already registered",
      errInvalidCredentials: "Wrong email or password",
      errMissingCredentials: "Enter email and password",
      errRateLimited: "Too many attempts. Wait a moment and try again.",
      errRateLimitedFor: "Too many attempts. Try again in {min} min.",
      errGeneric: "Error. Please try again.",
      errNetwork: "Network error",
      errNotVerified: "Please confirm your email first — we sent you a link.",
      resendVerification: "Resend confirmation email",
      verifySent: "Email sent. Check your inbox (and spam).",
      registerCheckEmail: "Almost done! Confirm your email via the link in your inbox.",
      verifiedOk: "Email confirmed — you can sign in now.",
      errVerifyInvalid: "The confirmation link is invalid or has expired.",
      errMailFailed: "Couldn't send the email. Please try again later.",
      docTitleReset: "Reset password — Artikel Drill",
      resetTitle: "Reset password",
      forgotPassword: "Forgot password?",
      resetRequestSub: "Enter your email and we'll send you a reset link.",
      sendResetLink: "Send link",
      resetSent: "If an account exists, an email has been sent. Check your spam folder too.",
      resetNewSub: "Enter a new password (at least 8 characters).",
      newPasswordPlaceholder: "New password",
      changePassword: "Change password",
      resetDone: "Password changed! Redirecting…",
      errResetInvalid: "The link is invalid or has expired. Request a new one.",
      backToLogin: "Back to sign-in",
      deleteAccountTitle: "Delete account",
      deleteAccountSub: "Enter your email and password to permanently delete your account and all statistics. This cannot be undone.",
      deleteForever: "Delete account permanently",
      backToApp: "Back to the app",
      confirmDeleteFull: "Really delete your account and all data? This cannot be undone.",
      accountDeleted: "Account deleted.",
      errDeleteFailedLater: "Couldn't delete the account. Try again later.",
    },

    ru: {
      language: "Язык",
      docTitle: "Artikel Drill",
      docTitleLogin: "Вход — Artikel Drill",
      docTitleDelete: "Удаление аккаунта — Artikel Drill",
      appTitle: "Artikel Drill",
      level: "Уровень: {level}",
      wordsPassed: "слов пройдено",
      progressTitle: "Прогресс до следующего уровня",
      allLevelsUnlocked: "Все уровни открыты 🎉",
      toNextLevel: "До уровня {level}: {m} / {n} слов ({pct}%)",
      correctExcl: "Верно!",
      correctPlural: "Правильно: Plural — {word}",
      correctArticle: "Правильно: {article} {word}{gloss}",
      registerNudge: "Не хочешь потерять прогресс и хочешь продолжить на других устройствах?",
      registerNudgeCta: "Зарегистрируйся!",
      keySpace: "Пробел",
      keyNext: "— дальше",
      statistics: "Статистика",
      account: "Аккаунт",
      signInLink: "Войти в аккаунт",
      registerLink: "Зарегистрироваться",
      syncOk: "Синхронизировано",
      syncPending: "Сохранение…",
      syncOffline: "Офлайн — сохранено локально, отправлю позже",
      close: "Закрыть",
      colWord: "Слово",
      colCorrectTitle: "Правильных ответов",
      colWrongTitle: "Неправильных ответов",
      colSeen: "Показов",
      colSeenTitle: "Сколько раз показано",
      jsonSummary: "Данные (JSON) — экспорт / импорт",
      copy: "Копировать",
      importFromField: "Импортировать из поля",
      resetStats: "Сбросить статистику",
      dataSummary: "{n} слов в статистике · всего в словаре: {total}",
      copied: "Скопировано",
      copyManual: "Выдели и скопируй вручную",
      errInvalidJson: "Ошибка: невалидный JSON",
      errExpectObject: "Ожидается объект",
      imported: "Импортировано",
      confirmReset: "Сбросить всю статистику? Это действие необратимо.",
      logout: "Выйти",
      privacyPolicy: "Политика конфиденциальности",
      deleteAccount: "Удалить аккаунт",
      signedInAs: "Вход выполнен: {email}",
      confirmLogout: "Выйти? Для входа снова понадобятся email и пароль.",
      confirmDelete1: "Удалить аккаунт и все данные без возможности восстановления?",
      confirmDelete2: "Точно удалить? Это действие необратимо.",
      errDeleteFailed: "Не удалось удалить аккаунт",
      errLoadDict: "Не удалось загрузить словарь",
      errLoadDictSub: "проверь, что сервер запущен, и обнови страницу",
      dictEmpty: "Словарь пуст",
      loginSub: "Вход в аккаунт",
      registerSub: "Регистрация",
      passwordPlaceholder: "Пароль",
      signIn: "Войти",
      createAccount: "Создать аккаунт",
      toggleToRegister: "Нет аккаунта? Зарегистрироваться",
      toggleToLogin: "Уже есть аккаунт? Войти",
      errInvalidEmail: "Некорректный email",
      errWeakPassword: "Пароль должен быть не короче 8 символов",
      errEmailTaken: "Такой email уже зарегистрирован",
      errInvalidCredentials: "Неверный email или пароль",
      errMissingCredentials: "Заполните email и пароль",
      errRateLimited: "Слишком много попыток. Подождите немного и попробуйте снова.",
      errRateLimitedFor: "Слишком много попыток. Попробуй снова через {min} мин.",
      errGeneric: "Ошибка. Попробуйте ещё раз.",
      errNetwork: "Ошибка сети",
      errNotVerified: "Сначала подтверди email — мы отправили тебе ссылку.",
      resendVerification: "Отправить письмо ещё раз",
      verifySent: "Письмо отправлено. Проверь почту (и папку «Спам»).",
      registerCheckEmail: "Почти готово! Подтверди email по ссылке из письма.",
      verifiedOk: "Email подтверждён — теперь можно войти.",
      errVerifyInvalid: "Ссылка подтверждения недействительна или устарела.",
      errMailFailed: "Не удалось отправить письмо. Попробуй позже.",
      docTitleReset: "Сброс пароля — Artikel Drill",
      resetTitle: "Сброс пароля",
      forgotPassword: "Забыли пароль?",
      resetRequestSub: "Введи email — пришлём ссылку для сброса пароля.",
      sendResetLink: "Отправить ссылку",
      resetSent: "Если аккаунт существует, письмо отправлено. Проверь и папку «Спам».",
      resetNewSub: "Введи новый пароль (не короче 8 символов).",
      newPasswordPlaceholder: "Новый пароль",
      changePassword: "Сменить пароль",
      resetDone: "Пароль изменён! Перенаправление…",
      errResetInvalid: "Ссылка недействительна или устарела. Запроси новую.",
      backToLogin: "Вернуться ко входу",
      deleteAccountTitle: "Удаление аккаунта",
      deleteAccountSub: "Введите email и пароль, чтобы навсегда удалить аккаунт и всю статистику. Действие необратимо.",
      deleteForever: "Удалить аккаунт навсегда",
      backToApp: "Вернуться в приложение",
      confirmDeleteFull: "Точно удалить аккаунт и все данные? Это необратимо.",
      accountDeleted: "Аккаунт удалён.",
      errDeleteFailedLater: "Не удалось удалить аккаунт. Попробуйте позже.",
    },
  };

  function detect() {
    try {
      var saved = localStorage.getItem(LS_LANG);
      if (SUPPORTED.indexOf(saved) !== -1) return saved;
    } catch (e) {}
    var nav = ((global.navigator && (navigator.languages && navigator.languages[0] || navigator.language)) || "")
      .slice(0, 2).toLowerCase();
    return SUPPORTED.indexOf(nav) !== -1 ? nav : FALLBACK;
  }

  var lang = detect();
  var listeners = [];

  function getLang() { return lang; }

  function t(key, params) {
    var table = STRINGS[lang] || STRINGS[FALLBACK];
    var s = table[key];
    if (s == null) s = STRINGS[FALLBACK][key];
    if (s == null) return key;                        // нет строки — показываем ключ (заметно при отладке)
    if (params) {
      s = s.replace(/\{(\w+)\}/g, function (m, k) {
        return params[k] != null ? String(params[k]) : m;
      });
    }
    return s;
  }

  // Применяем строки к статической разметке (атрибуты data-i18n*).
  function apply(root) {
    root = root || document;
    each(root.querySelectorAll("[data-i18n]"), function (e) {
      e.textContent = t(e.getAttribute("data-i18n"));
    });
    each(root.querySelectorAll("[data-i18n-title]"), function (e) {
      e.title = t(e.getAttribute("data-i18n-title"));
    });
    each(root.querySelectorAll("[data-i18n-placeholder]"), function (e) {
      e.placeholder = t(e.getAttribute("data-i18n-placeholder"));
    });
    each(root.querySelectorAll("[data-i18n-aria]"), function (e) {
      e.setAttribute("aria-label", t(e.getAttribute("data-i18n-aria")));
    });
    // переключатели языка: подсветка активного + подпись группы
    each(root.querySelectorAll(".lang-switch"), function (sw) {
      sw.setAttribute("aria-label", t("language"));
      each(sw.querySelectorAll("button[data-lang]"), function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
      });
    });
    if (document.documentElement) document.documentElement.lang = lang;
  }

  function setLang(l) {
    if (SUPPORTED.indexOf(l) === -1 || l === lang) return;
    lang = l;
    try { localStorage.setItem(LS_LANG, l); } catch (e) {}
    apply();
    for (var i = 0; i < listeners.length; i++) {
      try { listeners[i](l); } catch (e) {}
    }
  }

  function onChange(cb) { if (typeof cb === "function") listeners.push(cb); }

  // Переключатель de / en / ru. Стили вставляем один раз, чтобы работать одинаково на всех страницах.
  var styleInjected = false;
  function injectStyle() {
    if (styleInjected || !document.head) return;
    styleInjected = true;
    var css =
      ".lang-switch{display:inline-flex;gap:2px;align-items:center}" +
      ".lang-switch button{background:none;border:none;margin:0;padding:3px 7px;font:inherit;" +
      "font-size:13px;line-height:1;color:var(--muted,#9a9a9a);cursor:pointer;border-radius:6px;" +
      "-webkit-appearance:none;appearance:none}" +
      ".lang-switch button:hover{color:var(--ink,#2b2b2b)}" +
      ".lang-switch button[aria-pressed=\"true\"]{color:var(--ink,#2b2b2b);font-weight:700;background:var(--hover,#f5f5f4)}";
    var st = document.createElement("style");
    st.id = "i18n-style";
    st.textContent = css;
    document.head.appendChild(st);
  }

  function mountSwitcher(container) {
    if (!container) return;
    injectStyle();
    container.classList.add("lang-switch");
    container.setAttribute("role", "group");
    container.setAttribute("aria-label", t("language"));
    container.textContent = "";
    for (var i = 0; i < SUPPORTED.length; i++) {
      (function (code) {
        var b = document.createElement("button");
        b.type = "button";
        b.textContent = code.toUpperCase();
        b.setAttribute("data-lang", code);
        b.setAttribute("aria-pressed", String(code === lang));
        b.addEventListener("click", function () { setLang(code); });
        container.appendChild(b);
      })(SUPPORTED[i]);
    }
  }

  function each(list, fn) { for (var i = 0; i < list.length; i++) fn(list[i]); }

  // Применяем как можно раньше (и повторно на DOMContentLoaded — на случай раннего подключения в <head>).
  if (document.documentElement) document.documentElement.lang = lang;
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { apply(); });
  } else {
    apply();
  }

  global.I18N = {
    t: t, getLang: getLang, setLang: setLang, apply: apply,
    onChange: onChange, mountSwitcher: mountSwitcher, SUPPORTED: SUPPORTED,
  };
})(window);
