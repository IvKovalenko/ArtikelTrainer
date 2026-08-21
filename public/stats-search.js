/* Поиск по таблице статистики с автодополнением. Общий модуль для десктопного
   окна (app.js) и мобильной страницы (stats.html) — логика одна, чтобы версии
   не расходились (как AuthForm в auth-form.js). Ищем по немецкому слову (без
   артикля) и переводу среди строк, которые есть в таблице; выбор подсказки —
   прыжок к строке таблицы с кратковременной подсветкой.

   StatsSearch.mount({ input, list, tableBody, getItems, max? }) → { reset, refresh }
     input     — <input type="search">
     list      — <ul role="listbox"> под подсказки
     tableBody — <tbody> таблицы (у строк проставлен data-key)
     getItems  — () => [{ key, display, word, tr }] — актуальные строки таблицы
     max       — сколько подсказок показывать (по умолчанию 12) */
(function (global) {
  "use strict";

  // нижний регистр + снятие диакритики: «Übung» ищется по «ubung», «Grün» по «grun»
  function norm(s) {
    return (s == null ? "" : String(s)).toLowerCase()
      .normalize("NFD").replace(/\p{Diacritic}/gu, "");
  }

  function mount(opts) {
    var input = opts.input, list = opts.list, tableBody = opts.tableBody;
    var getItems = opts.getItems, max = opts.max || 12;
    if (!input || !list || !tableBody || typeof getItems !== "function") return null;

    var active = -1;   // индекс подсвеченной подсказки (-1 — ни одной)
    var current = [];  // элементы, показанные в списке сейчас

    function hide() {
      list.hidden = true;
      list.replaceChildren();
      current = [];
      active = -1;
      input.setAttribute("aria-expanded", "false");
    }

    function jumpTo(key) {
      // ищем строку перебором, а не селектором: ключи содержат пробелы и скобки
      // («Band (том)»), и экранирование под querySelector только мешало бы
      var rows = tableBody.querySelectorAll("tr");
      var row = null;
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].dataset.key === key) { row = rows[i]; break; }
      }
      if (!row) return;
      row.scrollIntoView({ block: "center" });   // мгновенно, без анимации прокрутки
      // перезапуск анимации подсветки: снять класс, форсировать reflow, навесить снова
      row.classList.remove("row-hit");
      void row.offsetWidth;
      row.classList.add("row-hit");
    }

    function pick(item) {
      if (!item) return;
      input.value = item.display;
      hide();
      jumpTo(item.key);
    }

    function setActive(i) {
      var lis = list.querySelectorAll('li[role="option"]');
      if (!lis.length) return;
      if (i < 0) i = lis.length - 1;
      if (i >= lis.length) i = 0;
      for (var j = 0; j < lis.length; j++) lis[j].setAttribute("aria-selected", String(j === i));
      active = i;
      if (lis[i].scrollIntoView) lis[i].scrollIntoView({ block: "nearest" });
    }

    function render(q) {
      var nq = norm(q.trim());
      if (!nq) { hide(); return; }
      var items = getItems();
      var starts = [], contains = [];
      for (var i = 0; i < items.length; i++) {
        var it = items[i], w = norm(it.word), tr = norm(it.tr);
        if (w.indexOf(nq) === 0 || tr.indexOf(nq) === 0) starts.push(it);        // совпадение с начала — выше
        else if (w.indexOf(nq) !== -1 || tr.indexOf(nq) !== -1) contains.push(it);
      }
      current = starts.concat(contains).slice(0, max);
      list.replaceChildren();

      if (!current.length) {
        var empty = document.createElement("li");
        empty.className = "s-empty";
        empty.setAttribute("aria-disabled", "true");
        empty.textContent = I18N.t("searchNoMatch");
        list.appendChild(empty);
        list.hidden = false;
        input.setAttribute("aria-expanded", "true");
        active = -1;
        return;
      }

      var frag = document.createDocumentFragment();
      for (var k = 0; k < current.length; k++) {
        (function (it) {
          var li = document.createElement("li");
          li.setAttribute("role", "option");
          li.setAttribute("aria-selected", "false");
          var sw = document.createElement("span");
          sw.className = "s-word";
          sw.textContent = it.display;
          var st = document.createElement("span");
          st.className = "s-tr";
          st.textContent = it.tr;
          li.appendChild(sw);
          li.appendChild(st);
          // pointerdown (до blur/click) — выбор срабатывает и мышью, и тапом,
          // а поле не теряет фокус раньше времени
          li.addEventListener("pointerdown", function (e) { e.preventDefault(); pick(it); });
          frag.appendChild(li);
        })(current[k]);
      }
      list.appendChild(frag);
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      active = -1;
    }

    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("focus", function () { if (input.value.trim()) render(input.value); });
    input.addEventListener("keydown", function (e) {
      if (list.hidden) return;
      if (e.key === "ArrowDown") { e.preventDefault(); setActive(active + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); }
      else if (e.key === "Enter") {
        var choice = (active >= 0 ? current[active] : current[0]);
        if (choice) { e.preventDefault(); pick(choice); }
      } else if (e.key === "Escape") { e.preventDefault(); hide(); }
    });
    // тап/клик мимо поля и списка — скрыть подсказки
    document.addEventListener("pointerdown", function (e) {
      if (e.target !== input && !list.contains(e.target)) hide();
    });

    hide();
    return {
      reset: function () { input.value = ""; hide(); },
      // перерисовать открытый список (напр. после смены языка — меняются переводы)
      refresh: function () { if (!list.hidden && input.value.trim()) render(input.value); },
    };
  }

  global.StatsSearch = { mount: mount };
})(window);
