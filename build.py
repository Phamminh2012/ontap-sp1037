"""Đọc cau-hoi.txt -> sinh on-thi-tthcm.html (tự chứa, mở offline được).

Định dạng cau-hoi.txt:
  # Chương N: tiêu đề
  ? câu hỏi
  + đáp án đúng
  - đáp án sai (3 dòng)
  > giải thích / nguồn (tuỳ chọn)
Chạy: python3 build.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent


def parse(text):
    chapters, qs, cur = [], [], None
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        tag, body = line[0], line[1:].strip()
        if tag == "#":
            m = re.match(r"Chương (\d+):\s*(.+)", body)
            if not m:
                sys.exit(f"Dòng {n}: tiêu đề chương sai định dạng")
            chapters.append({"n": int(m[1]), "t": m[2]})
        elif tag == "?":
            cur = {"c": chapters[-1]["n"], "q": body, "o": [], "e": "", "line": n}
            qs.append(cur)
        elif tag in "+-":
            # đáp án đúng luôn ở o[0]; HTML tự xáo trộn khi hiển thị
            (cur["o"].insert(0, body) if tag == "+" else cur["o"].append(body))
            cur.setdefault("ok", 0)
            cur["ok"] += tag == "+"
        elif tag == ">":
            cur["e"] = body
        else:
            sys.exit(f"Dòng {n}: không hiểu ký tự đầu '{tag}'")
    for q in qs:
        if q.get("ok") != 1 or len(q["o"]) != 4 or len(set(q["o"])) != 4:
            sys.exit(f"Dòng {q['line']}: cần đúng 1 đáp án '+' và 4 phương án khác nhau")
        del q["ok"], q["line"]
    return chapters, qs


def main():
    chapters, qs = parse((ROOT / "cau-hoi.txt").read_text(encoding="utf-8"))
    data = json.dumps({"ch": chapters, "qs": qs}, ensure_ascii=False, separators=(",", ":"))
    html = TEMPLATE.replace("/*DATA*/null", data.replace("</", "<\\/"))
    (ROOT / "on-thi-tthcm.html").write_text(html, encoding="utf-8")
    per = {c["n"]: sum(q["c"] == c["n"] for q in qs) for c in chapters}
    print(f"OK: {len(qs)} câu", per)


TEMPLATE = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ôn thi TTHCM</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1f;--mute:#6b6b70;--line:#e3e1dc;--acc:#b3261e;--acc2:#8c1d17;
--ok:#1e7d3a;--okbg:#e6f4ea;--bad:#b3261e;--badbg:#fce8e6;--sel:#fff4d6;--shadow:0 1px 3px rgba(0,0,0,.06)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141416;--card:#1e1e21;--ink:#ececee;--mute:#a1a1a8;
--line:#333338;--acc:#f2766b;--acc2:#ff9b92;--ok:#6fcf8a;--okbg:#17321f;--bad:#f2766b;--badbg:#3a1a18;--sel:#3a3320;--shadow:none}}
:root[data-theme="dark"]{--bg:#141416;--card:#1e1e21;--ink:#ececee;--mute:#a1a1a8;--line:#333338;--acc:#f2766b;--acc2:#ff9b92;
--ok:#6fcf8a;--okbg:#17321f;--bad:#f2766b;--badbg:#3a1a18;--sel:#3a3320;--shadow:none}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:16px 16px 80px}
header{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:4px 0 16px}
h1{font-size:20px;margin:0;letter-spacing:-.01em}
h1 small{display:block;font-size:13px;font-weight:400;color:var(--mute)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:14px;box-shadow:var(--shadow)}
h2{font-size:16px;margin:0 0 10px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:flex;align-items:flex-start;gap:8px;border:1px solid var(--line);border-radius:10px;padding:8px 10px;cursor:pointer;flex:1 1 300px;font-size:14px}
.chip input{margin-top:3px;accent-color:var(--acc)}
.chip b{white-space:nowrap}
.chip .n{color:var(--mute);margin-left:auto;white-space:nowrap}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
button,.btn{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:10px;padding:10px 14px;cursor:pointer}
button:hover{border-color:var(--mute)}
button.pri{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
button.pri:hover{background:var(--acc2)}
button:disabled{opacity:.45;cursor:default}
.opt:disabled{opacity:1}
button:focus-visible,.opt:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
.ghost{border:none;background:none;color:var(--mute);padding:6px 8px}
label.opt-line{display:flex;gap:8px;align-items:center;font-size:14px;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center}
.stats div{border:1px solid var(--line);border-radius:10px;padding:10px 4px}
.stats b{display:block;font-size:22px;font-variant-numeric:tabular-nums}
.stats span{font-size:12px;color:var(--mute)}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:8px 0 14px}
.bar i{display:block;height:100%;background:var(--acc);transition:width .2s}
.meta{display:flex;justify-content:space-between;font-size:13px;color:var(--mute);gap:8px;flex-wrap:wrap}
.timer{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink)}
.q{font-size:18px;font-weight:600;margin:6px 0 14px;line-height:1.45}
.opt{display:flex;gap:10px;width:100%;text-align:left;margin:8px 0;padding:12px 14px;border-radius:12px;line-height:1.45}
.opt .k{flex:none;width:24px;height:24px;border-radius:50%;border:1px solid var(--line);display:grid;place-items:center;font-size:13px;font-weight:600;color:var(--mute)}
.opt.sel{background:var(--sel);border-color:#d9a400}
.opt.ok{background:var(--okbg);border-color:var(--ok)}
.opt.ok .k{background:var(--ok);border-color:var(--ok);color:#fff}
.opt.bad{background:var(--badbg);border-color:var(--bad)}
.opt.bad .k{background:var(--bad);border-color:var(--bad);color:#fff}
.exp{margin-top:12px;padding:10px 12px;border-left:3px solid var(--acc);background:var(--bg);border-radius:6px;font-size:14px;color:var(--mute)}
.exp b{color:var(--ink)}
.nav{display:flex;justify-content:space-between;gap:8px;margin-top:14px}
.grid{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.grid button{width:38px;height:34px;padding:0;font-size:13px;border-radius:8px}
.grid .done{background:var(--sel)}.grid .g-ok{background:var(--okbg);border-color:var(--ok)}.grid .g-bad{background:var(--badbg);border-color:var(--bad)}
.grid .cur{outline:2px solid var(--acc)}
.big{font-size:44px;font-weight:700;text-align:center;margin:4px 0;font-variant-numeric:tabular-nums}
.center{text-align:center}
.mute{color:var(--mute);font-size:14px}
.tag{display:inline-block;font-size:12px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);color:var(--mute);margin-right:6px}
input[type=search]{font:inherit;width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink)}
.li{border-top:1px solid var(--line);padding:12px 0}
.li .a{color:var(--ok);font-weight:600}
mark{background:var(--sel);color:inherit}
.hidden{display:none!important}
kbd{font:12px ui-monospace,monospace;border:1px solid var(--line);border-radius:4px;padding:0 4px}
@media (max-width:480px){.q{font-size:17px}.big{font-size:36px}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Ôn thi Tư tưởng Hồ Chí Minh<small>SP1037 · Bách Khoa · Giáo trình Bộ GD&ĐT</small></h1>
  <button class="ghost" id="themeBtn" title="Đổi giao diện sáng/tối" aria-label="Đổi giao diện">◐</button>
</header>

<section id="home">
  <div class="card">
    <h2>Chọn chương</h2>
    <div class="chips" id="chapters"></div>
    <div class="row" style="margin-top:10px">
      <button class="ghost" id="allCh">Chọn tất cả</button><button class="ghost" id="noneCh">Bỏ chọn</button>
      <label class="opt-line" style="margin-left:auto"><input type="checkbox" id="onlyExam"> Chỉ câu có trong đề thi / quiz</label>
    </div>
  </div>
  <div class="card">
    <h2>Chế độ</h2>
    <div class="row">
      <button class="pri" id="startPractice">Luyện tập</button>
      <button id="startExam">Thi thử 40 câu · 50 phút</button>
      <button id="startWrong">Ôn câu đã sai (<span id="wrongN">0</span>)</button>
      <button id="startBrowse">Xem toàn bộ đáp án</button>
    </div>
    <p class="mute" style="margin:10px 0 0">Luyện tập: chọn là biết đúng sai ngay, có giải thích. Thi thử: giống đề thật, chấm điểm cuối bài.
    Phím tắt: <kbd>1</kbd>–<kbd>4</kbd> chọn, <kbd>Enter</kbd>/<kbd>→</kbd> câu tiếp, <kbd>←</kbd> câu trước.</p>
  </div>
  <div class="card">
    <h2>Tiến độ của bạn</h2>
    <div class="stats">
      <div><b id="stSeen">0</b><span>câu đã làm</span></div>
      <div><b id="stAcc">–</b><span>tỉ lệ đúng</span></div>
      <div><b id="stTotal">0</b><span>tổng số câu</span></div>
    </div>
    <div class="row" style="margin-top:10px"><button class="ghost" id="resetBtn">Xoá tiến độ</button></div>
  </div>
</section>

<section id="quiz" class="hidden">
  <div class="card">
    <div class="meta"><span id="qPos"></span><span id="qTag"></span><span class="timer" id="timer"></span></div>
    <div class="bar"><i id="bar"></i></div>
    <div class="q" id="qText"></div>
    <div id="opts"></div>
    <div id="exp" class="exp hidden"></div>
    <div class="nav">
      <button id="prevBtn">← Trước</button>
      <button class="ghost" id="quitBtn">Thoát</button>
      <button class="pri" id="nextBtn">Tiếp →</button>
    </div>
    <div class="grid" id="grid"></div>
  </div>
</section>

<section id="result" class="hidden">
  <div class="card center">
    <div class="mute" id="rTitle"></div>
    <div class="big" id="rScore"></div>
    <div class="mute" id="rDetail"></div>
    <div class="row" style="justify-content:center;margin-top:14px">
      <button class="pri" id="reviewBtn">Xem lại bài</button>
      <button id="retryWrongBtn">Làm lại câu sai</button>
      <button id="homeBtn">Về trang chính</button>
    </div>
  </div>
  <div class="card" id="rByCh"></div>
</section>

<section id="browse" class="hidden">
  <div class="card">
    <div class="row" style="margin-bottom:10px"><button id="browseBack">← Về</button><span class="mute" id="browseN"></span></div>
    <input type="search" id="search" placeholder="Tìm từ khoá trong câu hỏi / đáp án…">
    <div id="list"></div>
  </div>
</section>
</div>

<script>
const DATA = /*DATA*/null;
const QS = DATA.qs, CH = DATA.ch, KEY = 'tthcm-v1';
const $ = id => document.getElementById(id);
const hash = s => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) | 0; return 'q' + (h >>> 0).toString(36); };
QS.forEach(q => q.id = hash(q.q + q.o[0]));
const isExam = q => /Đề thi|Đề HK|Quiz|quiz|BKEL|Bài tập HK/.test(q.e);

// ---- lưu tiến độ (chỉ là tiện ích, mất cũng không sao) ----
let store = { stat: {}, ch: CH.map(c => c.n), onlyExam: false };
try { Object.assign(store, JSON.parse(localStorage.getItem(KEY)) || {}); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
function record(q, right) {
  const s = store.stat[q.id] || (store.stat[q.id] = { r: 0, w: 0, last: 0 });
  right ? s.r++ : s.w++; s.last = right ? 1 : -1; save();
}

// ---- theme ----
try { const t = localStorage.getItem(KEY + '-theme'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
$('themeBtn').onclick = () => {
  const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === 'dark'
    : matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = dark ? 'light' : 'dark';
  try { localStorage.setItem(KEY + '-theme', document.documentElement.dataset.theme); } catch (e) {}
};

// ---- home ----
function renderHome() {
  $('chapters').innerHTML = CH.map(c => {
    const n = QS.filter(q => q.c === c.n).length;
    return `<label class="chip"><input type="checkbox" value="${c.n}" ${store.ch.includes(c.n) ? 'checked' : ''}>
      <span><b>Chương ${c.n}.</b> ${c.t}</span><span class="n">${n} câu</span></label>`;
  }).join('');
  $('onlyExam').checked = store.onlyExam;
  const seen = Object.values(store.stat), r = seen.reduce((a, s) => a + s.r, 0), w = seen.reduce((a, s) => a + s.w, 0);
  $('stSeen').textContent = seen.length;
  $('stAcc').textContent = r + w ? Math.round(100 * r / (r + w)) + '%' : '–';
  $('stTotal').textContent = QS.length;
  $('wrongN').textContent = QS.filter(q => store.stat[q.id]?.last === -1).length;
}
$('chapters').onchange = () => { store.ch = [...$('chapters').querySelectorAll('input:checked')].map(i => +i.value); save(); };
$('onlyExam').onchange = e => { store.onlyExam = e.target.checked; save(); };
$('allCh').onclick = () => { store.ch = CH.map(c => c.n); save(); renderHome(); };
$('noneCh').onclick = () => { store.ch = []; save(); renderHome(); };
$('resetBtn').onclick = () => { if (confirm('Xoá toàn bộ tiến độ đã lưu?')) { store.stat = {}; save(); renderHome(); } };

const pool = () => QS.filter(q => store.ch.includes(q.c) && (!store.onlyExam || isExam(q)));
const shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; };
function show(id) { for (const s of ['home', 'quiz', 'result', 'browse']) $(s).classList.toggle('hidden', s !== id); scrollTo(0, 0); }

// ---- phiên làm bài ----
let S = null, tick = null;
function start(list, mode) {
  if (!list.length) return alert('Không có câu nào phù hợp. Hãy chọn thêm chương hoặc bỏ lọc.');
  S = { mode, items: list.map(q => ({ q, ord: shuffle([0, 1, 2, 3]), pick: null })), i: 0, end: null, done: false };
  if (mode === 'exam') S.end = Date.now() + 50 * 60 * 1000;
  clearInterval(tick); tick = S.end ? setInterval(updTimer, 1000) : null;
  show('quiz'); renderQ();
}
$('startPractice').onclick = () => start(shuffle(pool()), 'practice');
$('startExam').onclick = () => start(shuffle(pool()).slice(0, 40), 'exam');
$('startWrong').onclick = () => start(shuffle(QS.filter(q => store.stat[q.id]?.last === -1)), 'practice');

function updTimer() {
  if (!S || !S.end) return $('timer').textContent = '';
  const left = Math.max(0, S.end - Date.now()), m = left / 60000 | 0, s = (left / 1000 | 0) % 60;
  $('timer').textContent = `⏱ ${m}:${String(s).padStart(2, '0')}`;
  if (!left && !S.done) finish();
}
const revealed = it => S.done || (S.mode === 'practice' && it.pick !== null);

function renderQ() {
  const it = S.items[S.i], q = it.q, show_ = revealed(it);
  $('qPos').textContent = `Câu ${S.i + 1}/${S.items.length}`;
  $('qTag').textContent = `Chương ${q.c}`;
  $('bar').style.width = (100 * (S.i + 1) / S.items.length) + '%';
  $('qText').textContent = q.q;
  $('opts').innerHTML = '';
  it.ord.forEach((oi, k) => {
    const b = document.createElement('button');
    b.className = 'opt';
    if (show_ && oi === 0) b.classList.add('ok');
    else if (show_ && it.pick === oi) b.classList.add('bad');
    else if (!show_ && it.pick === oi) b.classList.add('sel');
    b.innerHTML = `<span class="k">${'ABCD'[k]}</span><span></span>`;
    b.lastChild.textContent = q.o[oi];
    b.onclick = () => pick(oi);
    b.disabled = show_;
    $('opts').append(b);
  });
  const e = $('exp');
  if (show_) {
    e.classList.remove('hidden');
    e.innerHTML = `<b>${it.pick === 0 ? '✓ Chính xác.' : it.pick === null ? 'Chưa trả lời.' : '✗ Sai.'}</b> Đáp án: <b></b>${q.e ? '<br>' : ''}<span></span>`;
    e.children[1].textContent = q.o[0]; e.lastChild.textContent = q.e;
  } else e.classList.add('hidden');
  $('prevBtn').disabled = S.i === 0;
  const last = S.i === S.items.length - 1;
  $('nextBtn').textContent = last ? (S.done ? 'Kết quả' : S.mode === 'exam' ? 'Nộp bài' : 'Kết thúc') : 'Tiếp →';
  $('grid').innerHTML = '';
  if (S.mode === 'exam' || S.done) S.items.forEach((x, j) => {
    const g = document.createElement('button');
    g.textContent = j + 1;
    if (S.done) g.className = x.pick === 0 ? 'g-ok' : 'g-bad'; else if (x.pick !== null) g.className = 'done';
    if (j === S.i) g.classList.add('cur');
    g.onclick = () => { S.i = j; renderQ(); };
    $('grid').append(g);
  });
  updTimer();
}
function pick(oi) {
  const it = S.items[S.i];
  if (revealed(it)) return;
  it.pick = oi;
  if (S.mode === 'practice') record(it.q, oi === 0);
  renderQ();
}
function next() {
  if (S.i < S.items.length - 1) { S.i++; renderQ(); return; }
  if (S.done) return show('result');
  if (S.mode === 'exam') {
    const left = S.items.filter(x => x.pick === null).length;
    if (left && !confirm(`Còn ${left} câu chưa làm. Nộp bài?`)) return;
  }
  finish();
}
$('nextBtn').onclick = next;
$('prevBtn').onclick = () => { if (S.i) { S.i--; renderQ(); } };
$('quitBtn').onclick = () => { if (S.done || confirm('Thoát phiên đang làm?')) { clearInterval(tick); S = null; renderHome(); show('home'); } };

function finish() {
  clearInterval(tick); S.done = true;
  if (S.mode === 'exam') S.items.forEach(x => record(x.q, x.pick === 0));
  const answered = S.items.filter(x => x.pick !== null), right = S.items.filter(x => x.pick === 0).length, n = S.items.length;
  $('rTitle').textContent = S.mode === 'exam' ? 'Kết quả thi thử' : 'Kết quả luyện tập';
  $('rScore').textContent = S.mode === 'exam' ? (10 * right / n).toFixed(2) + ' / 10' : `${right} / ${answered.length}`;
  $('rDetail').textContent = `Đúng ${right} · Sai ${answered.length - right} · Bỏ trống ${n - answered.length}`;
  $('rByCh').innerHTML = '<h2>Theo chương</h2>' + CH.map(c => {
    const xs = S.items.filter(x => x.q.c === c.n); if (!xs.length) return '';
    const r = xs.filter(x => x.pick === 0).length;
    return `<div class="meta" style="padding:6px 0;border-top:1px solid var(--line)"><span>Chương ${c.n}. ${c.t}</span><b>${r}/${xs.length}</b></div>`;
  }).join('');
  renderHome(); show('result');
}
$('reviewBtn').onclick = () => { S.i = 0; show('quiz'); renderQ(); };
$('retryWrongBtn').onclick = () => { const w = S.items.filter(x => x.pick !== 0).map(x => x.q); w.length ? start(shuffle(w), 'practice') : alert('Không có câu sai 🎉'); };
$('homeBtn').onclick = () => { renderHome(); show('home'); };

document.addEventListener('keydown', e => {
  if ($('quiz').classList.contains('hidden') || e.target.tagName === 'INPUT') return;
  const k = '1234'.indexOf(e.key) + 1 || 'abcd'.indexOf(e.key.toLowerCase()) + 1;
  if (k) { const it = S.items[S.i]; pick(it.ord[k - 1]); }
  else if (e.key === 'Enter' || e.key === 'ArrowRight') { e.preventDefault(); next(); }
  else if (e.key === 'ArrowLeft') $('prevBtn').click();
});

// ---- xem toàn bộ ----
const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function renderList() {
  const term = $('search').value.trim().toLowerCase();
  const hl = s => { const t = esc(s); if (!term) return t; const i = t.toLowerCase().indexOf(esc(term)); return i < 0 ? t : t.slice(0, i) + '<mark>' + t.slice(i, i + esc(term).length) + '</mark>' + t.slice(i + esc(term).length); };
  const xs = pool().filter(q => !term || (q.q + ' ' + q.o[0] + ' ' + q.e).toLowerCase().includes(term));
  $('browseN').textContent = `${xs.length} câu`;
  $('list').innerHTML = xs.map((q, i) => `<div class="li"><span class="tag">Ch.${q.c}</span><b>${i + 1}. ${hl(q.q)}</b>
    <div class="a">→ ${hl(q.o[0])}</div>${q.e ? `<div class="mute">${hl(q.e)}</div>` : ''}</div>`).join('');
}
$('startBrowse').onclick = () => { show('browse'); renderList(); };
$('search').oninput = renderList;
$('browseBack').onclick = () => show('home');

renderHome();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
