"use strict";
const { chapters, questions } = window.CNXH;
const byId = new Map(questions.map(q => [q.id, q]));
const app = document.getElementById("app");
const KEY = "cnxh-v1";

// ---------- Tiến độ lưu trong trình duyệt ----------
function load() {
  const empty = { stats: {}, stars: {}, opts: {} };
  try { return { ...empty, ...JSON.parse(localStorage.getItem(KEY)) }; } catch { return empty; }
}
const store = load();
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(store)); } catch { /* chế độ riêng tư: bỏ qua */ }
}
function record(q, correct) {
  const s = store.stats[q.id] || { right: 0, wrong: 0 };
  s[correct ? "right" : "wrong"]++;
  s.last = correct;
  store.stats[q.id] = s;
  save();
}

// ---------- Tiện ích ----------
function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  el.append(...kids.flat().filter(k => k !== null && k !== false && k !== undefined));
  return el;
}
const show = (...nodes) => app.replaceChildren(...nodes.flat().filter(Boolean));
function shuffle(list) {
  const a = [...list];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
// Không đảo câu có lựa chọn tham chiếu chữ cái ("Cả A, B, C...") hoặc câu Đúng/Sai
function optionOrder(q, mix) {
  const keys = Object.keys(q.o);
  const fixed = keys.length < 3 || Object.values(q.o).some(t => /(^|\s)C[ảàáâaã]\s+A\b|A,\s*B/i.test(t));
  return mix && !fixed ? shuffle(keys) : keys;
}
const letter = i => "ABCD"[i];
const plain = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/gi, "d").toLowerCase();

// ---------- Hiển thị một câu hỏi ----------
// order: thứ tự khóa gốc; chữ cái hiển thị luôn là A, B, C, D theo vị trí
function questionCard(q, order, { picked, reveal, onPick, label }) {
  const shown = k => letter(order.indexOf(k));
  const star = h("button", {
    title: "Đánh dấu để ôn lại", "aria-pressed": !!store.stars[q.id],
    onclick: () => {
      if (store.stars[q.id]) delete store.stars[q.id]; else store.stars[q.id] = 1;
      save();
      star.textContent = store.stars[q.id] ? "★ Đã đánh dấu" : "☆ Đánh dấu";
      star.setAttribute("aria-pressed", !!store.stars[q.id]);
    },
  }, store.stars[q.id] ? "★ Đã đánh dấu" : "☆ Đánh dấu");

  return h("div", { class: "card" },
    h("div", { class: "row between" },
      h("span", { class: "muted" }, `${label ? label + " · " : ""}Câu ${q.id} · Chương ${q.c}`), star),
    h("div", { class: "question" }, q.q),
    q.cut !== undefined && h("div", { class: "info" },
      "Đề gốc bị thiếu chữ." + (q.cut ? ` Gợi ý (phỏng đoán): ${q.cut}` : "")),
    order.map((k, i) => {
      let cls = "opt";
      if (reveal && k === q.a) cls += " right";
      else if (reveal && k === picked) cls += " wrong";
      else if (k === picked) cls += " picked";
      return h("button", { class: cls, disabled: reveal || !onPick, onclick: onPick && (() => onPick(k)) },
        h("b", {}, letter(i) + "."), h("span", {}, q.o[k]));
    }),
    reveal && !picked && h("div", { class: "muted" }, `Đáp án đúng: ${shown(q.a)}`),
    reveal && q.unsure && h("div", { class: "info" },
      "Cần xác nhận: đáp án này đã được sửa nhưng giáo trình không đề cập. Nên hỏi giảng viên."),
    reveal && q.orig && h("div", { class: "muted" },
      `Đề gốc ghi đáp án: ${q.orig.split(",").map(k => q.o[k.trim()]).join(" / ")}` +
      (q.page ? ` · Đã sửa theo giáo trình tr.${q.page}` : "")),
    reveal && q.note && h("div", { class: "info" }, q.note),
  );
}

// ---------- Bộ chọn chương ----------
function chapterPicker(selected, onChange) {
  return h("div", { class: "card" }, chapters.map(ch => {
    const list = questions.filter(q => q.c === ch.chapter);
    const right = list.filter(q => store.stats[q.id]?.last === true).length;
    const wrong = list.filter(q => store.stats[q.id]?.last === false).length;
    return h("label", { class: "chapter" },
      h("input", {
        type: "checkbox", checked: selected.has(ch.chapter),
        onchange: e => { e.target.checked ? selected.add(ch.chapter) : selected.delete(ch.chapter); onChange(); },
      }),
      h("span", {}, `Chương ${ch.chapter}. ${ch.title}`),
      h("span", { class: "muted" }, `${right}/${list.length}`),
      h("span", { class: "bar", title: `${right} đúng, ${wrong} sai` },
        h("i", { class: "good", style: `width:${right / list.length * 100}%` }),
        h("i", { class: "poor", style: `width:${wrong / list.length * 100}%` })),
    );
  }));
}
function savedChapters() {
  return new Set(store.opts.chapters ?? chapters.map(c => c.chapter));
}
function check(name, text, fallback) {
  return h("label", {}, h("input", {
    type: "checkbox", checked: store.opts[name] ?? fallback,
    onchange: e => { store.opts[name] = e.target.checked; save(); },
  }), " " + text);
}

// ---------- Luyện tập ----------
const SOURCES = {
  all: ["Tất cả câu", () => true],
  new: ["Câu chưa làm", q => !store.stats[q.id]],
  wrong: ["Câu đang sai", q => store.stats[q.id]?.last === false],
  star: ["Câu đã đánh dấu", q => store.stars[q.id]],
  fixed: ["Câu đã sửa đáp án", q => q.orig],
};
let session = null; // phiên luyện tập hoặc thi đang mở

function home() {
  const selected = savedChapters();
  const pool = () => questions.filter(q => selected.has(q.c) && SOURCES[source.value][1](q));
  const source = h("select", { onchange: () => update() },
    Object.entries(SOURCES).map(([v, [t]]) => h("option", { value: v }, t)));
  const start = h("button", {
    class: "primary",
    onclick: () => {
      const list = store.opts.random ? shuffle(pool()) : pool();
      session = { type: "practice", list, i: 0, picks: {}, orders: {} };
      practice();
    },
  });
  function update() {
    store.opts.chapters = [...selected];
    save();
    const n = pool().length;
    start.textContent = `Bắt đầu (${n} câu)`;
    start.disabled = n === 0;
  }
  const done = Object.keys(store.stats).length;
  const right = Object.values(store.stats).filter(s => s.last).length;

  show(
    h("h1", {}, "Luyện tập"),
    h("p", { class: "muted" }, `Đã làm ${done}/${questions.length} câu, đang đúng ${right}. Chọn đáp án là biết kết quả ngay.`),
    chapterPicker(selected, update),
    h("div", { class: "card row between" },
      h("div", { class: "row" }, source, check("random", "Trộn câu", false), check("mix", "Đảo đáp án", false)),
      start),
    h("button", {
      onclick: () => {
        if (!confirm("Xóa toàn bộ tiến độ và câu đã đánh dấu?")) return;
        store.stats = {}; store.stars = {}; save(); home();
      },
    }, "Xóa tiến độ"),
  );
  update();
}

function practice() {
  const s = session;
  const q = s.list[s.i];
  s.orders[q.id] ??= optionOrder(q, store.opts.mix);
  const picked = s.picks[q.id];
  const values = Object.entries(s.picks);
  const correct = values.filter(([id, k]) => byId.get(id).a === k).length;
  const go = i => { s.i = Math.max(0, Math.min(s.list.length - 1, i)); practice(); };
  s.pick = k => {
    if (s.picks[q.id]) return;
    s.picks[q.id] = k;
    record(q, k === q.a);
    practice();
  };
  s.order = s.orders[q.id];
  s.next = () => go(s.i + 1);
  s.prev = () => go(s.i - 1);

  show(
    h("div", { class: "row between muted" },
      h("span", {}, `${s.i + 1}/${s.list.length}`),
      h("span", {}, `Đúng ${correct}/${values.length}`)),
    questionCard(q, s.order, { picked, reveal: !!picked, onPick: s.pick }),
    h("div", { class: "row between" },
      h("button", { onclick: s.prev, disabled: s.i === 0 }, "← Trước"),
      h("button", { onclick: () => { session = null; home(); } }, "Kết thúc"),
      h("button", { class: "primary", onclick: s.next, disabled: s.i === s.list.length - 1 }, "Tiếp →")),
    h("p", { class: "muted" }, "Phím tắt: A–D hoặc 1–4 để chọn, ← → hoặc Enter để chuyển câu."),
  );
}

// ---------- Thi thử ----------
// Chia số câu theo tỉ lệ từng chương (phần dư lớn nhất)
function sample(chs, count) {
  const groups = chs.map(c => shuffle(questions.filter(q => q.c === c)));
  const total = groups.reduce((n, g) => n + g.length, 0);
  const n = Math.min(count, total);
  const quota = groups.map(g => g.length / total * n);
  const take = quota.map(Math.floor);
  quota.map((v, i) => [v - take[i], i]).sort((a, b) => b[0] - a[0])
    .slice(0, n - take.reduce((a, b) => a + b, 0)).forEach(([, i]) => take[i]++);
  return shuffle(groups.flatMap((g, i) => g.slice(0, take[i])));
}

function examSetup() {
  if (session?.type === "exam") return exam();
  const selected = savedChapters();
  const count = h("input", { type: "number", min: 1, max: questions.length, value: store.opts.count ?? 40 });
  const minutes = h("input", { type: "number", min: 0, max: 300, value: store.opts.minutes ?? 45 });
  const start = h("button", {
    class: "primary",
    onclick: () => {
      const n = Math.max(1, parseInt(count.value, 10) || 40);
      const m = Math.max(0, parseInt(minutes.value, 10) || 0);
      Object.assign(store.opts, { count: n, minutes: m });
      save();
      const list = sample([...selected], n);
      session = {
        type: "exam", list, i: 0, picks: {},
        orders: Object.fromEntries(list.map(q => [q.id, optionOrder(q, store.opts.examMix ?? true)])),
        end: m ? Date.now() + m * 60000 : null,
      };
      exam();
    },
  }, "Bắt đầu thi");
  show(
    h("h1", {}, "Thi thử"),
    h("p", { class: "muted" }, "Câu hỏi lấy ngẫu nhiên theo tỉ lệ từng chương. Đáp án chỉ hiện sau khi nộp bài."),
    chapterPicker(selected, () => { store.opts.chapters = [...selected]; save(); start.disabled = !selected.size; }),
    h("div", { class: "card row between" },
      h("div", { class: "row" },
        h("label", {}, "Số câu ", count),
        h("label", {}, "Phút (0 = không giới hạn) ", minutes),
        check("examMix", "Đảo đáp án", true)),
      start),
  );
  start.disabled = !selected.size;
}

function clock(ms) {
  const t = Math.max(0, Math.ceil(ms / 1000));
  return `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(t % 60).padStart(2, "0")}`;
}

function exam() {
  const s = session;
  if (s.end && Date.now() >= s.end) return submit();
  const q = s.list[s.i];
  const go = i => { s.i = Math.max(0, Math.min(s.list.length - 1, i)); exam(); };
  s.order = s.orders[q.id];
  s.pick = k => { s.picks[q.id] = k; exam(); };
  s.next = () => go(s.i + 1);
  s.prev = () => go(s.i - 1);
  const answered = Object.keys(s.picks).length;

  show(
    h("div", { class: "row between sticky" },
      h("span", {}, `Đã trả lời ${answered}/${s.list.length}`),
      s.end && h("b", { id: "clock" }, clock(s.end - Date.now())),
      h("button", {
        class: "primary",
        onclick: () => {
          const left = s.list.length - answered;
          if (!left || confirm(`Còn ${left} câu chưa trả lời. Vẫn nộp bài?`)) submit();
        },
      }, "Nộp bài")),
    questionCard(q, s.order, { picked: s.picks[q.id], reveal: false, onPick: s.pick, label: `${s.i + 1}/${s.list.length}` }),
    h("div", { class: "row between" },
      h("button", { onclick: s.prev, disabled: s.i === 0 }, "← Trước"),
      h("button", { onclick: () => { if (confirm("Hủy bài thi này?")) { session = null; examSetup(); } } }, "Hủy bài"),
      h("button", { onclick: s.next, disabled: s.i === s.list.length - 1 }, "Tiếp →")),
    h("h2", {}, "Danh sách câu"),
    h("div", { class: "grid" }, s.list.map((x, i) => h("button", {
      class: `${s.picks[x.id] ? "done" : ""} ${i === s.i ? "current" : ""}`,
      onclick: () => go(i),
    }, String(i + 1)))),
  );
}

function submit() {
  const s = session;
  session = null;
  // Câu bỏ trống tính là sai trong điểm, nhưng không ghi vào tiến độ
  s.list.forEach(q => { if (s.picks[q.id]) record(q, s.picks[q.id] === q.a); });
  const right = s.list.filter(q => s.picks[q.id] === q.a).length;
  const missed = s.list.filter(q => s.picks[q.id] !== q.a);
  show(
    h("h1", {}, "Kết quả"),
    h("div", { class: "card" },
      h("div", { class: "score" }, `${(right / s.list.length * 10).toFixed(1)} / 10`),
      h("div", {}, `Đúng ${right}/${s.list.length} câu.`),
      chapters.map(ch => {
        const list = s.list.filter(q => q.c === ch.chapter);
        return list.length > 0 && h("div", { class: "muted" },
          `Chương ${ch.chapter}: ${list.filter(q => s.picks[q.id] === q.a).length}/${list.length}`);
      })),
    h("button", { class: "primary", onclick: examSetup }, "Thi đề khác"),
    missed.length > 0 && h("h2", {}, `Câu sai hoặc bỏ trống (${missed.length})`),
    missed.map(q => questionCard(q, s.orders[q.id], { picked: s.picks[q.id], reveal: true })),
  );
  window.scrollTo(0, 0);
}

// ---------- Tra cứu ----------
function search() {
  const input = h("input", { type: "search", placeholder: "Tìm theo nội dung hoặc số câu (không cần dấu)", oninput: () => run(true) });
  const chapter = h("select", { onchange: () => run(true) },
    h("option", { value: "" }, "Mọi chương"),
    chapters.map(c => h("option", { value: c.chapter }, `Chương ${c.chapter}`)));
  const results = h("div");
  let limit = 30;
  function run(reset) {
    if (reset) limit = 30;
    const term = plain(input.value.trim());
    const found = questions.filter(q =>
      (!chapter.value || q.c === Number(chapter.value)) &&
      (!term || q.id === term || plain([q.q, ...Object.values(q.o)].join(" ")).includes(term)));
    results.replaceChildren(
      h("p", { class: "muted" }, `${found.length} câu`),
      ...found.slice(0, limit).map(q => questionCard(q, Object.keys(q.o), { picked: null, reveal: true })),
    );
    if (found.length > limit) {
      results.append(h("button", { onclick: () => { limit += 50; run(false); } }, "Xem thêm"));
    }
  }
  show(h("h1", {}, "Tra cứu"), h("div", { class: "row" }, input, chapter), results);
  run(true);
}

// ---------- Điều hướng ----------
function route() {
  const page = location.hash.slice(1) || "home";
  document.querySelectorAll("[data-nav]").forEach(a => a.classList.toggle("on", a.dataset.nav === page));
  if (page === "exam") return examSetup();
  if (session?.type === "practice" && page === "home") return practice();
  if (page === "search") return search();
  home();
}
addEventListener("hashchange", route);

document.addEventListener("keydown", e => {
  const page = location.hash.slice(1) || "home";
  const active = session && ((session.type === "practice" && page === "home") || (session.type === "exam" && page === "exam"));
  if (!active || e.ctrlKey || e.metaKey || e.altKey) return;
  const i = "abcd".indexOf(e.key.toLowerCase()) >= 0 ? "abcd".indexOf(e.key.toLowerCase()) : "1234".indexOf(e.key);
  if (i >= 0 && session.order[i]) session.pick(session.order[i]);
  else if (e.key === "ArrowRight" || (e.key === "Enter" && e.target === document.body)) session.next();
  else if (e.key === "ArrowLeft") session.prev();
});

setInterval(() => {
  if (session?.type !== "exam" || !session.end) return;
  if (Date.now() >= session.end) {
    history.replaceState(null, "", "#exam");
    submit();
    return;
  }
  const el = document.getElementById("clock");
  if (el) el.textContent = clock(session.end - Date.now());
}, 500);

route();
