/* Общая форма входа/регистрации. Используется в двух местах:
   страница login.html (мобильные) и модальное окно на главной (десктоп).
   Логика одна, чтобы ошибки, rate-limit и подтверждение почты вели себя одинаково.

   AuthForm.mount(container, {
     mode: "login" | "register",     // стартовый режим
     showSub: true|false,            // подзаголовок режима внутри формы (в модалке его заменяет заголовок окна)
     onSuccess(data),                // токен получен и уже сохранён в localStorage
     onModeChange(mode),             // вызывается при переключении вход/регистрация
   }) → { setMode, getMode, setMsg, focus }

   Локальный анонимный прогресс при входе НЕ стирается: app.js сольёт его
   с серверным (mergeMax) и отправит обратно на сервер. */
(function (global) {
  "use strict";

  const LS_TOKEN = "auth-token";

  const ERRORS = {
    "invalid-email": "errInvalidEmail",
    "weak-password": "errWeakPassword",
    "email-taken": "errEmailTaken",
    "invalid-credentials": "errInvalidCredentials",
    "missing-credentials": "errMissingCredentials",
    "rate-limited": "errRateLimited",
    "email-not-verified": "errNotVerified",
    "mail-failed": "errMailFailed",
    "mail-not-configured": "errMailFailed",
  };
  // при rate-limit сервер присылает retryAfter (сек) — показываем, сколько ждать
  function errText(data) {
    if (data.error === "rate-limited" && data.retryAfter)
      return I18N.t("errRateLimitedFor", { min: Math.ceil(data.retryAfter / 60) });
    return I18N.t(ERRORS[data.error] || "errGeneric");
  }

  // стили формы — вставляем один раз, чтобы модалка и login.html выглядели одинаково
  let styleInjected = false;
  function injectStyle() {
    if (styleInjected || !document.head) return;
    styleInjected = true;
    const css =
      ".auth-form{display:flex;flex-direction:column;gap:12px;text-align:center}" +
      ".auth-form .sub{margin:0 0 4px;color:var(--muted,#9a9a9a);font-size:14px}" +
      ".auth-form input{width:100%;padding:14px;font:inherit;font-size:17px;color:var(--ink,#2b2b2b);" +
      "background:#fff;border:1px solid var(--line,#dcdcdc);border-radius:var(--radius,10px)}" +
      ".auth-form input:focus{outline:none;border-color:var(--line-hover,#bdbdbd)}" +
      ".auth-form .primary{width:100%;padding:14px;font:inherit;font-size:17px;color:#fff;" +
      "background:var(--ink,#2b2b2b);border:none;border-radius:var(--radius,10px);cursor:pointer;transition:opacity .12s ease}" +
      ".auth-form .primary:hover{opacity:.88}" +
      ".auth-form .primary:disabled{opacity:.5;cursor:default}" +
      ".auth-form .toggle{background:none;border:none;color:var(--muted,#9a9a9a);font:inherit;font-size:14px;" +
      "cursor:pointer;padding:4px;text-decoration:none;display:inline-block}" +
      ".auth-form .toggle[hidden]{display:none}" +   /* авторский display перебивал атрибут hidden */
      ".auth-form .toggle:hover{color:var(--ink,#2b2b2b);text-decoration:underline}" +
      ".auth-form .msg{min-height:20px;font-size:14px;color:var(--red,#e03131)}" +
      ".auth-form .msg.ok{color:var(--green,#2f9e44)}";
    const st = document.createElement("style");
    st.id = "auth-form-style";
    st.textContent = css;
    document.head.appendChild(st);
  }

  function mount(container, opts) {
    opts = opts || {};
    injectStyle();

    const form = document.createElement("form");
    form.className = "auth-form";
    form.autocomplete = "on";

    const sub = document.createElement("p");
    sub.className = "sub";
    if (opts.showSub === false) sub.hidden = true;

    const email = document.createElement("input");
    email.type = "email";
    email.name = "email";
    email.autocomplete = "email";
    email.placeholder = "Email";
    email.setAttribute("aria-label", "Email");
    email.required = true;

    const pw = document.createElement("input");
    pw.type = "password";
    pw.name = "password";
    pw.required = true;
    pw.minLength = 8;

    const submit = document.createElement("button");
    submit.type = "submit";
    submit.className = "primary";

    const msg = document.createElement("div");
    msg.className = "msg";

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "toggle";

    const resend = document.createElement("button");
    resend.type = "button";
    resend.className = "toggle";
    resend.hidden = true;

    const forgot = document.createElement("a");
    forgot.className = "toggle";
    forgot.href = "/reset-password.html";

    form.append(sub, email, pw, submit, msg, toggle, resend, forgot);
    container.appendChild(form);

    let mode = opts.mode === "register" ? "register" : "login";

    function setMsg(text, ok) {
      msg.textContent = text || "";
      msg.className = "msg" + (ok ? " ok" : "");
    }

    // Тексты, зависящие от режима и языка (i18n их сам не перерисует).
    function renderMode() {
      pw.placeholder = I18N.t("passwordPlaceholder");
      pw.setAttribute("aria-label", I18N.t("passwordPlaceholder"));
      resend.textContent = I18N.t("resendVerification");
      forgot.textContent = I18N.t("forgotPassword");
      if (mode === "login") {
        sub.textContent = I18N.t("loginSub");
        submit.textContent = I18N.t("signIn");
        pw.autocomplete = "current-password";
        toggle.textContent = I18N.t("toggleToRegister");
      } else {
        sub.textContent = I18N.t("registerSub");
        submit.textContent = I18N.t("createAccount");
        pw.autocomplete = "new-password";
        toggle.textContent = I18N.t("toggleToLogin");
      }
    }
    function setMode(m) {
      mode = m === "register" ? "register" : "login";
      renderMode();
      setMsg("");
      resend.hidden = true;
      if (opts.onModeChange) opts.onModeChange(mode);
    }
    toggle.addEventListener("click", () => setMode(mode === "login" ? "register" : "login"));

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      setMsg("");
      resend.hidden = true;
      submit.disabled = true;
      try {
        const r = await fetch("/api/auth/" + mode, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ email: email.value.trim(), password: pw.value }),
        });
        const data = await r.json().catch(() => ({}));
        if (r.ok && data.token) {
          localStorage.setItem(LS_TOKEN, data.token);
          // прогресс НЕ трогаем: локальные ответы вольются в аккаунт при загрузке
          if (opts.onSuccess) opts.onSuccess(data);
          return;                                   // submit остаётся disabled — идёт переход/перезагрузка
        }
        if (r.ok && data.verify) {                  // регистрация ок → ждём подтверждения почты
          setMode("login");
          setMsg(I18N.t("registerCheckEmail"), true);
          submit.disabled = false;
          return;
        }
        setMsg(errText(data));
        if (data.error === "email-not-verified") resend.hidden = false;
      } catch {
        setMsg(I18N.t("errNetwork"));
      }
      submit.disabled = false;
      pw.select();
    });

    // повторная отправка письма подтверждения (кнопка видна после errNotVerified)
    resend.addEventListener("click", async () => {
      resend.disabled = true;
      try {
        const r = await fetch("/api/auth/resend", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ email: email.value.trim() }),
        });
        const data = await r.json().catch(() => ({}));
        if (r.ok) { setMsg(I18N.t("verifySent"), true); resend.hidden = true; }
        else setMsg(errText(data));
      } catch {
        setMsg(I18N.t("errNetwork"));
      }
      resend.disabled = false;
    });

    I18N.onChange(renderMode);
    renderMode();
    if (opts.onModeChange) opts.onModeChange(mode);

    return {
      setMode,
      getMode: () => mode,
      setMsg,
      focus: () => email.focus(),
    };
  }

  global.AuthForm = { mount };
})(window);
