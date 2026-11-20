/* ============================================================
   SmartAudit-Quantum — Dashboard Vòng 2
   Đọc kết quả THẬT do scripts/export_dashboard.py xuất ra (data/*.json).
   "Kiểm tra khẳng định" chạy đúng mã nguồn Python của pipeline ngay trong
   trình duyệt bằng Pyodide — không cần server.
   ============================================================ */

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";

const V = {
  "nhất quán": { cls: "ok", label: "Nhất quán" },
  "mâu thuẫn": { cls: "review", label: "Cần xem xét" },
  "không kiểm chứng được": { cls: "unk", label: "Chưa kiểm chứng được" },
};

const METRIC_VI = {
  revenue_net: "Doanh thu thuần", profit_before_tax: "Lợi nhuận trước thuế",
  profit_after_tax: "Lợi nhuận sau thuế", gross_profit: "Lợi nhuận gộp",
  gross_margin: "Biên lợi nhuận gộp", net_margin: "Biên lợi nhuận ròng",
  cost_of_goods_sold: "Giá vốn hàng bán", selling_expense: "Chi phí bán hàng",
  admin_expense: "Chi phí quản lý doanh nghiệp", financial_expense: "Chi phí tài chính",
  interest_expense: "Chi phí lãi vay", total_assets: "Tổng tài sản",
  owners_equity: "Vốn chủ sở hữu", inventories: "Hàng tồn kho",
  cash_and_equivalents: "Tiền và tương đương tiền", inventory_turnover: "Vòng quay hàng tồn kho",
  selling_expense_ratio: "Biên chi phí bán hàng", admin_expense_ratio: "Biên chi phí quản lý",
};
const INFO_DIMS = new Set(["continuity", "scope", "lookup"]);
const PAGES = {
  overview: "Tổng quan", companies: "Doanh nghiệp", report: "Chi tiết báo cáo",
  check: "Kiểm tra khẳng định", evaluation: "Đánh giá chất lượng",
  quantum: "Thí nghiệm lượng tử", about: "Giới thiệu & dữ liệu",
};

const S = { results: [], facts: {}, metrics: null, examples: [] };

/* ── Tiện ích ── */
const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const nf = (x, d = 0) => (x == null ? "—" : Number(x).toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d }));
const pct = (x, d = 1) => (x == null ? "—" : `${nf(x * 100, d)}%`);
const metricVi = (k) => METRIC_VI[k] || k;
const badge = (v) => `<span class="vbadge ${V[v]?.cls || "unk"}">${V[v]?.label || esc(v)}</span>`;

async function getJSON(path) {
  const res = await fetch(path, { cache: "no-cache" });
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json();
}

/* ── Điều hướng ── */
function switchPage(page) {
  if (!PAGES[page]) page = "overview";
  document.querySelectorAll(".page").forEach((p) => p.classList.toggle("active", p.id === `page-${page}`));
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.toggle("active", n.dataset.page === page));
  $("#page-title").textContent = PAGES[page];
  setMenu(false);
  if (location.hash !== `#${page}`) history.replaceState(null, "", `#${page}`);
  if (page === "check") ensurePy().catch(() => {});
}

function setMenu(open) {
  $("#sidebar").classList.toggle("open", open);
  $("#sidebar-backdrop").hidden = !open;
  $("#menu-btn").setAttribute("aria-expanded", String(open));
}

/* ── Thẻ khẳng định ── */
function evidenceHTML(e) {
  const cls = INFO_DIMS.has(e.dimension) ? "info" : e.passed ? "pass" : "fail";
  const src = e.source_code ? ` <span class="src">· Mã số ${esc(e.source_code)}${e.source_page ? `, trang ${e.source_page} BCTC` : ""}</span>` : "";
  return `<div class="ev ${cls}">${esc(e.explanation)}${src}</div>`;
}

function claimHTML(c, ctx) {
  const v = V[c.verdict] || V["không kiểm chứng được"];
  const where = ctx ? `<b>${esc(ctx.ticker)} ${ctx.year}</b> · ` : "";
  return `<div class="claim ${v.cls}">
    <div class="claim-top">${badge(c.verdict)} ${where}${esc(metricVi(c.metric))}${c.page ? ` · BCTN trang ${c.page}` : " · câu nhập tay"}</div>
    <div class="claim-quote">“${esc(c.text)}”</div>
    ${(c.evidence || []).map(evidenceHTML).join("")}
  </div>`;
}

/* ── Tổng quan ── */
function renderOverview() {
  const p = S.metrics.pipeline;
  const now = p.verdicts_now;
  const total = p.claims_now;
  // Thẻ tóm tắt: bên trái là phạm vi dữ liệu, bên phải là kết quả đối chiếu
  // (một thanh chia ba phần, cùng bộ màu với danh sách doanh nghiệp bên dưới).
  const parts = [
    ["ok", "Nhất quán", now["nhất quán"], "khớp số liệu BCTC"],
    ["review", "Cần xem xét", now["mâu thuẫn"], "tín hiệu để người xem lại"],
    ["unk", "Chưa kiểm chứng được", now["không kiểm chứng được"], "im lặng có lý do"],
  ];
  $("#summary").innerHTML = `
    <div class="sum-scope">
      <div><b>${p.companies}</b><span>doanh nghiệp</span></div>
      <div><b>${p.reports}</b><span>báo cáo đối chiếu</span></div>
      <div><b>${nf(total)}</b><span>khẳng định trích được</span></div>
    </div>
    <div class="sum-verdict">
      <div class="sum-bar">${parts.filter(([, , n]) => n > 0)
        .map(([k, , n]) => `<span class="seg ${k}" style="flex:${n}"></span>`).join("")}</div>
      <div class="sum-legend">${parts.map(([k, label, n, hint]) => `
        <div><i class="sw ${k}"></i><b>${nf(n)}</b><span>${label}</span><small>${pct(total ? n / total : 0, 0)} · ${hint}</small></div>`).join("")}
      </div>
    </div>`;

  renderCompanyBars();

  const flagged = [];
  for (const r of S.results) for (const c of r.claims) if (c.verdict === "mâu thuẫn") flagged.push([r, c]);
  const sel = $("#review-filter");
  const tickers = [...new Set(flagged.map(([r]) => r.ticker))].sort();
  sel.innerHTML = `<option value="">Tất cả doanh nghiệp (${flagged.length})</option>` +
    tickers.map((t) => `<option value="${t}">${t} (${flagged.filter(([r]) => r.ticker === t).length})</option>`).join("");
  sel.onchange = () => renderReviewList(flagged);
  renderReviewList(flagged);
}

/* Phân bố phán quyết theo doanh nghiệp: mỗi hàng một thanh mảnh chia ba phần
   (nhất quán · cần xem xét · chưa kiểm chứng), số ghi bằng chữ bên phải để
   không phụ thuộc vào màu. Doanh nghiệp nhiều câu cần xem xét nhất lên đầu;
   ngân hàng (ngoài phạm vi) gom vào một dòng chú thích. */
function renderCompanyBars() {
  const by = {};
  for (const r of S.results) {
    const t = (by[r.ticker] ||= { ok: 0, review: 0, unk: 0, bank: r.bank, sector: r.sector, years: 0 });
    t.ok += r.counts["nhất quán"]; t.review += r.counts["mâu thuẫn"]; t.unk += r.counts["không kiểm chứng được"];
    t.years += 1;
  }
  const inScope = Object.keys(by).filter((t) => !by[t].bank);
  const banks = Object.keys(by).filter((t) => by[t].bank).sort();
  inScope.sort((a, b) => (by[b].review - by[a].review) || (by[b].ok - by[a].ok) || a.localeCompare(b));
  const pctOf = (n, total) => (total ? (100 * n) / total : 0);
  const num = (n, cls, sym, title) =>
    `<span class="${n === 0 ? "zero" : cls}" title="${title}">${sym} ${n}</span>`;

  $("#company-bars").innerHTML = inScope.map((t) => {
    const d = by[t]; const total = d.ok + d.review + d.unk;
    const segs = [["ok", d.ok], ["review", d.review], ["unk", d.unk]].filter(([, n]) => n > 0)
      .map(([k, n]) => `<span class="seg ${k}" style="flex:${pctOf(n, total).toFixed(2)}"></span>`).join("");
    const tip = `${t}: ${d.ok} nhất quán · ${d.review} cần xem xét · ${d.unk} chưa kiểm chứng (${total} khẳng định, ${d.years} năm)`;
    return `<div class="cb-row" data-t="${t}" title="${esc(tip)}">
      <div class="cb-name"><b>${t}</b><small>${esc(d.sector)}</small></div>
      <div class="cb-bar">${segs}</div>
      <div class="cb-nums">${num(d.ok, "", "✓", "nhất quán")}${num(d.review, "flag", "!", "cần xem xét")}${num(d.unk, "", "?", "chưa kiểm chứng")}</div>
    </div>`;
  }).join("");
  $("#company-bars-note").innerHTML =
    `Tổng số khẳng định của mỗi doanh nghiệp qua các năm có báo cáo. Bấm một hàng để lọc danh sách câu cần xem xét bên dưới.` +
    (banks.length ? ` Ngân hàng (${banks.join(", ")}) lập BCTC theo Thông tư 49, nằm ngoài phạm vi nên không đưa vào biểu đồ.` : "");

  $("#company-bars").onclick = (ev) => {
    const row = ev.target.closest(".cb-row");
    if (!row) return;
    const t = row.dataset.t;
    const sel = $("#review-filter");
    const same = sel.value === t;
    sel.value = same ? "" : ([...sel.options].some((o) => o.value === t) ? t : "");
    sel.onchange();
    document.querySelectorAll(".cb-row").forEach((r) => r.classList.toggle("active", !same && r.dataset.t === t));
    if (!same) $("#review-list").closest(".card").scrollIntoView({ behavior: "smooth", block: "start" });
  };
}

function renderReviewList(flagged) {
  const pick = $("#review-filter").value;
  const shown = pick ? flagged.filter(([r]) => r.ticker === pick) : flagged;
  $("#review-count").textContent = `· ${shown.length} câu`;
  $("#review-list").innerHTML = (shown.length
    ? shown.map(([r, c]) => claimHTML(c, r)).join("")
    : `<div class="empty-state"><p>Không có câu nào cần xem xét.</p></div>`);
}

/* ── Doanh nghiệp: bảng theo năm ──
   Mỗi ô là một báo cáo thường niên, tô theo trạng thái (có câu cần xem xét ·
   khớp hết · chưa kiểm chứng được) và ghi số câu ✓/! bằng chữ để không phụ
   thuộc vào màu. Ô không đối chiếu được ghi rõ lý do (bản scan, thiếu BCTC…). */
function renderCompanies() {
  const years = [...new Set(S.results.map((r) => r.year))].sort();
  const missing = S.metrics.pipeline.missing || {};
  const byKey = Object.fromEntries(S.results.map((r) => [`${r.ticker}_${r.year}`, r]));
  const info = {};
  for (const r of S.results) {
    const t = (info[r.ticker] ||= { review: 0, ok: 0, bank: r.bank, sector: r.sector });
    t.review += r.counts["mâu thuẫn"]; t.ok += r.counts["nhất quán"];
  }
  const all = Object.keys(info);
  const inScope = all.filter((t) => !info[t].bank)
    .sort((a, b) => (info[b].review - info[a].review) || (info[b].ok - info[a].ok) || a.localeCompare(b));
  const banks = all.filter((t) => info[t].bank).sort();

  const cell = (t, y) => {
    const r = byKey[`${t}_${y}`];
    if (!r) {
      const m = missing[`${t}_${y}`];
      return `<td class="hc c-none" title="${esc(m ? m.why : "Không có báo cáo thường niên của năm này")}"></td>`;
    }
    const n = r.counts, ok = n["nhất quán"], rv = n["mâu thuẫn"], unk = n["không kiểm chứng được"];
    const cls = rv ? "c-review" : ok ? "c-ok" : "c-unk";
    const tip = `${t} ${y}: ${ok} nhất quán · ${rv} cần xem xét · ${unk} chưa kiểm chứng được. Bấm để xem từng câu.`;
    const main = ok || rv
      ? `${ok ? `<span class="k-ok">✓ ${ok}</span>` : ""}${rv ? `<span class="k-review">! ${rv}</span>` : ""}`
      : `<span class="k-unk">—</span>`;
    return `<td class="hc ${cls}" data-t="${t}" data-y="${y}" title="${esc(tip)}"><div class="hc-main">${main}</div><small>${ok + rv + unk} câu</small></td>`;
  };
  const row = (t) => `<tr class="${info[t].bank ? "bank" : ""}"><th scope="row"><b>${t}</b><small>${esc(info[t].sector)}</small></th>${years.map((y) => cell(t, y)).join("")}</tr>`;
  $("#heat-table").innerHTML = `<colgroup><col class="col-name">${years.map(() => "<col>").join("")}</colgroup>
    <thead><tr><th></th>${years.map((y) => `<th>${y}</th>`).join("")}</tr></thead>
    <tbody>${inScope.map(row).join("")}
    ${banks.length ? `<tr class="group"><td colspan="${years.length + 1}">Ngân hàng lập BCTC theo Thông tư 49, nằm ngoài phạm vi đối chiếu nên mọi câu đều “chưa kiểm chứng được”</td></tr>${banks.map(row).join("")}` : ""}</tbody>`;
  $("#heat-table").onclick = (ev) => {
    const td = ev.target.closest("td.hc[data-t]");
    if (td) openReport(td.dataset.t, Number(td.dataset.y));
  };
}

/* ── Chi tiết báo cáo ── */
let reportFilter = "all";
const GROUPS = [["mâu thuẫn", "review", "Cần xem xét"], ["nhất quán", "ok", "Nhất quán"], ["không kiểm chứng được", "unk", "Chưa kiểm chứng được"]];

/* Tên tệp BCTC (vd. FPT_Baocaotaichinh_2018_Kiemtoan_Hopnhat) → mô tả dễ đọc. */
function sourceLabel(src, year) {
  if (!src) return "";
  const kind = /Hopnhat/i.test(src) ? " hợp nhất" : /Rieng|Congtyme/i.test(src) ? " riêng" : "";
  const audited = /Kiemtoan/i.test(src) ? " đã kiểm toán" : "";
  return `BCTC${kind}${audited} năm ${year}`;
}

function fillTickerYear(tSel, ySel, keys, onChange) {
  const tickers = [...new Set(keys.map((k) => k.split("_")[0]))].sort();
  tSel.innerHTML = tickers.map((t) => `<option>${t}</option>`).join("");
  const fillYears = () => {
    const ys = keys.filter((k) => k.startsWith(tSel.value + "_")).map((k) => k.split("_")[1]).sort();
    ySel.innerHTML = ys.map((y) => `<option>${y}</option>`).join("");
    ySel.value = ys[ys.length - 1];
  };
  tSel.onchange = () => { fillYears(); onChange(); };
  ySel.onchange = onChange;
  fillYears();
}

function renderReport() {
  const ySel = $("#report-year");
  $("#report-years").innerHTML = [...ySel.options].map((o) =>
    `<button class="ychip${o.value === ySel.value ? " active" : ""}" data-y="${o.value}" role="tab" aria-selected="${o.value === ySel.value}">${o.value}</button>`).join("");
  const r = S.results.find((x) => x.ticker === $("#report-ticker").value && x.year === Number(ySel.value));
  if (!r) return;
  const src = S.facts[`${r.ticker}_${r.year}`]?.source || "";
  const n = r.counts;
  const total = r.claims.length;
  if (reportFilter !== "all" && !n[reportFilter]) reportFilter = "all";
  $("#report-summary").innerHTML = `
    <div class="rep-head">
      <div class="rep-id"><b>${r.ticker} · ${r.year}</b><span>${esc(r.sector)}</span></div>
      <div class="rep-src" title="${esc(src)}">Câu trong báo cáo thường niên được đối chiếu với <b>${esc(sourceLabel(src, r.year))}</b>
        ${r.bank ? "<br>Ngân hàng lập BCTC theo Thông tư 49, nằm ngoài phạm vi đối chiếu." : ""}</div>
    </div>
    ${total ? `<div class="sum-bar">${GROUPS.filter(([v]) => n[v]).map(([v, cls]) => `<span class="seg ${cls}" style="flex:${n[v]}"></span>`).join("")}</div>` : ""}
    <div class="rep-filters">
      <button class="rf${reportFilter === "all" ? " active" : ""}" data-f="all">Tất cả <b>${total}</b></button>
      ${GROUPS.map(([v, cls, label]) => `<button class="rf${reportFilter === v ? " active" : ""}" data-f="${v}"${n[v] ? "" : " disabled"}><i class="sw ${cls}"></i>${label} <b>${n[v]}</b></button>`).join("")}
    </div>`;

  const of = (v) => r.claims.filter((c) => c.verdict === v);
  let html;
  if (!total) {
    html = `<div class="empty-state"><p>Không trích được khẳng định nào từ báo cáo này.</p></div>`;
  } else if (reportFilter === "all") {
    const onlyUnk = !n["mâu thuẫn"] && !n["nhất quán"];
    html = GROUPS.map(([v, , label]) => {
      const cs = of(v);
      if (!cs.length) return "";
      const body = cs.map((c) => claimHTML(c)).join("");
      return v === "không kiểm chứng được"
        ? `<details class="claim-group"${onlyUnk ? " open" : ""}><summary>${label} <b>${cs.length}</b>
            <span>Hệ thống chưa đủ căn cứ nên không kết luận. Bấm để xem lý do từng câu.</span></summary>${body}</details>`
        : `<div class="group-title">${label} <b>${cs.length}</b></div>${body}`;
    }).join("");
  } else {
    html = of(reportFilter).map((c) => claimHTML(c)).join("");
  }
  $("#report-claims").innerHTML = html;
}

function openReport(ticker, year) {
  $("#report-ticker").value = ticker;
  $("#report-ticker").onchange();
  $("#report-year").value = String(year);
  reportFilter = "all";
  renderReport();
  switchPage("report");
}

function setupReportPage() {
  fillTickerYear($("#report-ticker"), $("#report-year"), S.results.map((r) => `${r.ticker}_${r.year}`),
    () => { reportFilter = "all"; renderReport(); });
  $("#report-years").onclick = (ev) => {
    const b = ev.target.closest(".ychip");
    if (!b) return;
    $("#report-year").value = b.dataset.y;
    reportFilter = "all";
    renderReport();
  };
  $("#report-summary").onclick = (ev) => {
    const b = ev.target.closest(".rf");
    if (!b || b.disabled) return;
    reportFilter = b.dataset.f;
    renderReport();
  };
  renderReport();
}

/* ── Kiểm tra khẳng định: Pyodide ── */
let py = null;
let pyLoading = null;

const GLUE = `
import sys, json
sys.path.insert(0, "/home/pyodide")
from smartaudit.nlp import extract_claims
from smartaudit.nnc import check_claim
from smartaudit.nnc.checker import Fact, Unit
from smartaudit.tables import Statement

def sa_check(text, year, facts_json):
    raw = json.loads(facts_json)
    facts = {k: Fact(concept=v["concept"], current=v["current"], previous=v["previous"],
                     page=v["page"], code=v["code"], label=v["label"],
                     statement=Statement(v["statement"]), unit=Unit(v["unit"]))
             for k, v in raw.items()}
    claims = extract_claims("===== PAGE 1 =====\\n" + text.strip() + "\\n", default_year=int(year))
    out = []
    for c in claims:
        r = check_claim(c, facts)
        out.append({"metric": c.metric, "trend": c.trend.value, "value": c.value,
                    "percent": c.percent, "period": c.period, "is_ratio": c.is_ratio,
                    "text": c.text, "page": None, "verdict": r.verdict.value, "score": r.score,
                    "evidence": [{"dimension": e.dimension, "explanation": e.explanation,
                                  "passed": e.passed, "source_page": e.source_page,
                                  "source_code": e.source_code} for e in r.evidence]})
    return json.dumps(out, ensure_ascii=False)
`;

function loadScript(src) {
  return new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = src; s.onload = ok; s.onerror = () => fail(new Error(`Không tải được ${src}`));
    document.head.appendChild(s);
  });
}

async function ensurePy() {
  if (py) return py;
  if (pyLoading) return pyLoading;
  pyLoading = (async () => {
    try {
      if (!window.loadPyodide) await loadScript(PYODIDE_URL + "pyodide.js");
      const p = await window.loadPyodide({ indexURL: PYODIDE_URL });
      const files = await getJSON("data/py_files.json");
      for (const rel of files) {
        const text = await (await fetch("py/" + rel)).text();
        const parts = ("/home/pyodide/" + rel).split("/");
        for (let i = 2; i < parts.length; i++) {
          const dir = parts.slice(0, i).join("/");
          try { p.FS.mkdir(dir); } catch (_) { /* đã có */ }
        }
        p.FS.writeFile("/home/pyodide/" + rel, text);
      }
      p.runPython(GLUE);
      py = p;
      return p;
    } catch (err) {
      pyLoading = null;
      throw new Error(`Không nạp được lõi Python (${err.message}). Cần kết nối mạng tới cdn.jsdelivr.net.`);
    }
  })();
  return pyLoading;
}

async function runCheck() {
  const text = $("#check-text").value.trim();
  const key = `${$("#check-ticker").value}_${$("#check-year").value}`;
  const box = $("#check-result");
  if (!text) { box.innerHTML = `<div class="empty-state"><p>Hãy nhập một câu.</p></div>`; return; }
  box.innerHTML = `<div class="empty-state"><p>Đang đối chiếu…</p></div>`;
  try {
    const p = await ensurePy();
    const facts = S.facts[key]?.facts || {};
    const out = JSON.parse(p.globals.get("sa_check")(text, Number($("#check-year").value), JSON.stringify(facts)));
    if (!out.length) {
      box.innerHTML = `<div class="claim"><div class="claim-top">${badge("không kiểm chứng được")}</div>
        <div class="claim-quote">Hệ thống không nhận diện được khẳng định đối chiếu được trong câu này.</div>
        <div class="ev info">Câu phải nêu một chỉ tiêu (doanh thu, lợi nhuận, tổng tài sản, chi phí…) kèm giá trị, tỷ lệ hoặc hướng biến động của năm báo cáo.</div>
        <div class="ev info">Câu về công ty con, một mảng/thị trường, kế hoạch tương lai, chính sách kế toán, số liệu theo quý hoặc năm khác bị loại <b>có chủ đích</b> — thà im lặng còn hơn cáo buộc sai.</div></div>`;
      return;
    }
    box.innerHTML = `<p class="note check-src">Đối chiếu với <b>${esc($("#check-ticker").value)} · ${esc(sourceLabel(S.facts[key]?.source, $("#check-year").value) || key)}</b></p>` +
      out.map((c) => claimHTML(c)).join("");
  } catch (err) {
    box.innerHTML = `<div class="empty-state"><p>${esc(err.message)}</p></div>`;
  }
}

const LOAI_VI = { gia_tri: "sửa con số", phan_tram: "sửa tỷ lệ %", huong: "đảo tăng ↔ giảm", kiem_soat_chi_phi: "nói sai về chi phí" };

function renderCheck() {
  fillTickerYear($("#check-ticker"), $("#check-year"), Object.keys(S.facts), () => {});
  $("#check-run").onclick = runCheck;
  const btn = ([e, i]) => `<button class="example" data-i="${i}"><span class="tag${e.real ? "" : " synthetic"}">${e.ticker} ${e.year} · ${
    e.real ? (e.page ? `BCTN trang ${e.page}` : "BCTN") : LOAI_VI[e.loai] || "đã sửa"}</span>${esc(e.text)}</button>`;
  const all = S.examples.map((e, i) => [e, i]);
  const real = all.filter(([e]) => e.real), fake = all.filter(([e]) => !e.real);
  $("#examples").innerHTML =
    (real.length ? `<div class="ex-group"><div class="lbl">Câu thật trong báo cáo thường niên</div>${real.map(btn).join("")}</div>` : "") +
    (fake.length ? `<div class="ex-group"><div class="lbl">Câu đã sửa sai để thử <span class="muted">(không có trong báo cáo)</span></div>${fake.map(btn).join("")}</div>` : "");
  $("#examples").onclick = (ev) => {
    const b = ev.target.closest(".example");
    if (!b) return;
    const e = S.examples[Number(b.dataset.i)];
    $("#check-ticker").value = e.ticker;
    $("#check-ticker").onchange();
    $("#check-year").value = String(e.year);
    $("#check-text").value = e.text;
    runCheck();
  };
}

/* ── Đánh giá: phép thử cố tình viết sai ── */
/* Đánh dấu chỗ khác nhau giữa câu gốc và câu đã sửa (sửa một từ/số), chỉ giữ
   vài từ quanh chỗ sửa để ví dụ ngắn gọn. */
function diffSnippet(orig, changed, around = 4) {
  const a = orig.split(/\s+/), b = changed.split(/\s+/);
  let i = 0;
  while (i < Math.min(a.length, b.length) && a[i] === b[i]) i++;
  if (i >= b.length) return esc(changed);
  const from = Math.max(0, i - around), to = Math.min(b.length, i + around + 1);
  return (from > 0 ? "… " : "") + b.slice(from, to).map((w, k) => (from + k === i ? `<mark>${esc(w)}</mark>` : esc(w))).join(" ") + (to < b.length ? " …" : "");
}

/* Thanh ngang chia hai phần (bắt được · bỏ lọt) hoặc một phần trên nền 0–100%. */
function hbarRow({ name, desc, tag, segs, value, sub, best }) {
  return `<div class="hb-row${best ? " best" : ""}">
    <div class="hb-name"><b>${name}${tag || ""}</b>${desc ? `<small>${desc}</small>` : ""}</div>
    <div class="hb-track">${segs.filter((s) => s.n > 0).map((s) => `<span class="seg ${s.cls}" style="flex:${s.n}"></span>`).join("")}</div>
    <div class="hb-val"><b>${value}</b>${sub ? `<small>${sub}</small>` : ""}</div>
  </div>`;
}

function renderEvaluation() {
  const inj = S.metrics.injected;
  if (!inj) { $("#eval-steps").innerHTML = `<p class="note">Chưa có kết quả phép thử.</p>`; return; }
  const r = inj.recall_chen_loi;
  const ctrl = inj.bao_dong_gia_doi_chung;
  const vd = inj.vi_du;
  const lech05 = (inj.chi_tiet || []).find((d) => d.loai === "doi_chung" && d.muc.startsWith("lech"));

  $("#eval-steps").innerHTML = `
    <li><b>Lấy câu đúng</b><span>Câu thật trong báo cáo thường niên mà hệ thống đã xác nhận khớp với BCTC kiểm toán.</span></li>
    <li><b>Cố tình sửa cho sai</b><span>Đổi con số, đổi tỷ lệ %, đảo “tăng” thành “giảm”, hoặc viết “chi phí được kiểm soát tốt” khi chi phí thực ra tăng nhanh hơn doanh thu.</span></li>
    <li><b>Cho hệ thống đọc lại</b><span>Đếm xem bao nhiêu câu sai bị gắn “Cần xem xét”. Song song, giữ nguyên ${nf(ctrl.n)} câu đúng để xem hệ thống có báo nhầm không.</span></li>`;

  if (vd) {
    const kinds = [["gia_tri", "Sửa con số"], ["phan_tram", "Sửa tỷ lệ %"], ["huong", "Đảo chiều"]];
    $("#eval-demo").innerHTML = `
      <div class="demo-label">Ví dụ · câu thật của ${esc(vd.ticker)} ${vd.year}</div>
      <div class="demo-orig"><span class="vbadge ok">Câu gốc · Nhất quán</span><p>“${esc(vd.goc)}”</p></div>
      ${kinds.filter(([k]) => vd.bien_the[k]).map(([k, label]) => {
        const v = vd.bien_the[k];
        const caught = v.ket_qua === "mâu thuẫn";
        return `<div class="demo-row"><span class="demo-kind">${label}</span>
          <span class="demo-text">${diffSnippet(vd.goc, v.text)}</span>
          <span class="demo-res ${caught ? "hit" : "miss"}">${caught ? "✓ bị bắt" : "✗ lọt"}</span></div>`;
      }).join("")}`;
  }

  $("#eval-kpis").innerHTML = `
    <div class="big-kpi good"><b>${pct(r.ty_le, 0)}</b><div><span>câu viết sai bị bắt</span>
      <small>${nf(r.dung)} trên ${nf(r.n)} câu đã cố tình sửa sai</small></div></div>
    <div class="big-kpi good"><b>${nf(ctrl.n - ctrl.dung)}</b><div><span>câu đúng bị báo nhầm</span>
      <small>trên ${nf(ctrl.n)} câu đúng${lech05 ? `, trong đó ${nf(lech05.n)} câu chỉ lệch 0,5% do làm tròn` : ""}</small></div></div>`;

  const types = [
    ["gia_tri", "Sai con số", "lệch từ 2% đến 20% so với số đúng"],
    ["phan_tram", "Sai tỷ lệ %", "lệch từ 2 đến 10 điểm phần trăm"],
    ["huong", "Đảo chiều tăng/giảm", "“tăng” thành “giảm” hoặc ngược lại"],
    ["kiem_soat_chi_phi", "Nói sai về chi phí", "“chi phí được kiểm soát tốt” trong khi chi phí trên doanh thu tăng quá 2 điểm"],
  ].filter(([k]) => inj.recall_theo_loai[k]?.n);
  $("#eval-types").innerHTML = types.map(([k, name, desc]) => {
    const t = inj.recall_theo_loai[k];
    return hbarRow({ name, desc, segs: [{ cls: "caught", n: t.dung }, { cls: "missed", n: t.n - t.dung }],
      value: pct(t.ty_le, 0), sub: `bắt ${nf(t.dung)}/${nf(t.n)} câu` });
  }).join("");

  // Sai càng nhỏ càng khó bắt: gộp các mức ± của phép sửa con số.
  const byLevel = {};
  for (const d of inj.chi_tiet || []) {
    if (d.loai !== "gia_tri") continue;
    const lv = d.muc.replace(/[+-]/, "");
    (byLevel[lv] ||= { n: 0, dung: 0 });
    byLevel[lv].n += d.n; byLevel[lv].dung += d.dung;
  }
  const levels = Object.entries(byLevel).sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]));
  const gold = S.metrics.evaluation?.gold_distribution;
  $("#eval-note").innerHTML =
    (levels.length >= 2 ? `<b>Sai càng nhỏ càng khó bắt:</b> ${levels.map(([lv, x]) => `lệch ${lv.replace(".", ",")} bắt ${pct(x.dung / x.n, 0)}`).join(" · ")}. ` : "") +
    `<br><b>Vì sao phải tự tạo câu sai?</b> Báo cáo thật rất hiếm khi viết sai số liệu đã kiểm toán` +
    (gold ? ` (trong ${nf(S.metrics.evaluation.n_labeled)} câu thật đội đã đọc và gán nhãn, chỉ ${nf(gold.MT)} câu mâu thuẫn thật)` : "") +
    `, nên không đủ để đo. Đây là câu sửa nhân tạo: đo độ nhạy của hệ thống, không phải tỷ lệ sai ngoài thực tế.`;
}

/* ── Lượng tử ── */
function renderQuantum() {
  const q = S.metrics.quantum;
  if (!q) { $("#qka-intro").innerHTML = `<p class="note">Chưa có kết quả.</p>`; return; }
  const ds = q.dataset || {};
  const cls = Object.fromEntries((ds.classes || []).map((c) => [c.code, c]));
  const pair = [["23", "tiền ra", /^Tiền chi/], ["24", "tiền vào", /^Tiền thu hồi/]].filter(([c]) => cls[c]);
  $("#qka-intro").innerHTML = `
    <div class="prose">
      <p>Hệ thống tìm đúng ô số liệu trong BCTC nhờ cột <b>Mã số</b>. Nhưng một số bảng (bản OCR) bị mất cột này,
        khi đó phải đọc <b>tên dòng</b> để đoán đó là khoản mục nào.</p>
      <p>Khó ở chỗ cùng một khoản mục có hàng chục cách viết, và có những cặp tên gần giống nhau nhưng nghĩa ngược nhau.</p>
      <p>Đội lấy <b>${nf(ds.n_samples)} cách viết khác nhau</b> của ${nf((ds.classes || []).length)} khoản mục trong phần dòng tiền đầu tư,
        từ ${nf(ds.n_rows)} dòng BCTC thật của ${nf((ds.tickers || []).length)} doanh nghiệp, rồi cho bốn cách đoán thi với nhau.</p>
    </div>
    ${pair.length === 2 ? `<div class="q-pair">
      ${pair.map(([code, dir, re]) => `<div class="q-name"><span>“${esc(cls[code].most_common_name).replace(re, (m) => `<mark>${m}</mark>`)}”</span>
        <em>Mã ${code} · ${dir}</em></div>`).join("")}
      <p class="note">Chỉ khác vài chữ, nhưng đoán nhầm là đảo chiều dòng tiền.</p>
    </div>` : ""}`;

  const M = q.methods;
  const methods = [
    ["svm_rbf", "Máy học cổ điển (SVM)", "học cách phân biệt từ các tên đã biết", false],
    ["qsvm_qka", "Lượng tử có học (QKA)", "mạch 8 qubit tự điều chỉnh để phân biệt tên", true],
    ["rapidfuzz_top8", "So khớp chữ (rapidfuzz)", "so độ giống nhau của chữ, như hệ thống đang dùng", false],
    ["qsvm_fixed", "Lượng tử cố định", "mạch 8 qubit không điều chỉnh", true],
  ].filter(([k]) => M[k]).sort((a, b) => M[b[0]].accuracy_mean - M[a[0]].accuracy_mean);
  const best = methods[0][0];
  const secs = (s) => (s < 0.05 ? "tức thì" : `${nf(s, s < 10 ? 1 : 0)} giây`);
  $("#qka-bars").innerHTML = methods.map(([k, name, desc, quantum]) => {
    const acc = M[k].accuracy_mean * 100;
    return hbarRow({
      name, desc, best: k === best,
      tag: ` <span class="kind ${quantum ? "quantum" : "classic"}">${quantum ? "Lượng tử" : "Cổ điển"}</span>${k === best ? ` <span class="kind best">Tốt nhất</span>` : ""}`,
      segs: [{ cls: quantum ? "quantum" : "classic", n: acc }, { cls: "rest", n: 100 - acc }],
      value: `${nf(acc, 0)}%`, sub: `học mất ${secs(M[k].train_seconds_mean)}`,
    });
  }).join("");
  $("#qka-bars-note").textContent = `Tỷ lệ đoán đúng trên những tên chưa từng thấy khi học (trung bình ${q.n_folds} lần chia dữ liệu). Thanh tính từ 0 đến 100%.`;

  const svm = M.svm_rbf, qka = M.qsvm_qka, fixed = M.qsvm_fixed, fuzz = M.rapidfuzz_top8;
  const slower = svm && qka ? Math.round(qka.train_seconds_mean / svm.train_seconds_mean / 10) * 10 : null;
  const items = [];
  if (svm && qka) items.push(["Cổ điển vẫn thắng", `Máy học cổ điển đoán đúng ${pct(svm.accuracy_mean, 0)}; lượng tử tốt nhất đúng ${pct(qka.accuracy_mean, 0)} và học chậm hơn khoảng ${nf(slower)} lần.`]);
  if (fixed && qka) items.push(["Cho lượng tử học thì có tiến bộ", `Từ ${pct(fixed.accuracy_mean, 0)} với mạch cố định lên ${pct(qka.accuracy_mean, 0)} khi mạch được tự điều chỉnh (QKA).`]);
  items.push(["Đây là kiểm chứng kỹ thuật", `Chạy trên máy mô phỏng ${q.n_qubits} qubit nên chưa thể có lợi thế lượng tử. Phần lượng tử tháo rời được: hệ thống chạy đủ mà không cần nó.`]);
  if (svm && fuzz) items.push(["Lợi ích thực tế", `Máy học cổ điển đoán tốt hơn cách so khớp chữ đang dùng (${pct(svm.accuracy_mean, 0)} so với ${pct(fuzz.accuracy_mean, 0)}). Đây là hướng cải thiện tiếp theo cho hệ thống.`]);
  $("#qka-text").innerHTML = items.map(([t, d], i) => `<div class="q-card"><em>${i + 1}</em><b>${t}</b><p>${d}</p></div>`).join("");

  const rows = [...methods.map(([k, n]) => [k, n]), ["rapidfuzz_1nn", "So khớp chữ, mọi tên đã biết (tham khảo)"], ["svm_linear_full", "SVM tuyến tính, không nén (tham khảo)"]].filter(([k]) => M[k]);
  $("#qka-tech").innerHTML = `<summary>Số liệu kỹ thuật</summary>
    <div class="card-body">
      <table class="simple"><thead><tr><th>Phương pháp</th><th>Accuracy</th><th>Macro-F1</th><th>Huấn luyện / phần</th></tr></thead><tbody>
      ${rows.map(([k, n]) => { const m = M[k]; return `<tr class="${k === best ? "best" : ""}"><td>${n}</td>
        <td class="num">${nf(m.accuracy_mean, 3)} ± ${nf(m.accuracy_std, 3)}</td><td class="num">${nf(m.macro_f1_mean, 3)}</td>
        <td class="num">${nf(m.train_seconds_mean, 2)} s</td></tr>`; }).join("")}
      </tbody></table>
      <p class="note">${q.n_qubits} qubit · mô phỏng statevector (Qiskit), không nhiễu · kiểm chứng chéo ${q.n_folds} phần, chia theo tên để không tên nào nằm ở cả hai phía ·
        ${nf(ds.n_samples)} mẫu · tổng thời gian chạy ${nf((q.total_seconds || 0) / 60, 1)} phút.
        Kernel alignment trên tập huấn luyện: cố định ${nf(q.alignment?.qka_train_before?.mean, 3)} → QKA ${nf(q.alignment?.qka_train_after?.mean, 3)} (RBF ${nf(q.alignment?.rbf_train?.mean, 3)}).</p>
    </div>`;
}

/* ── Khởi động ── */
async function init() {
  document.querySelectorAll(".nav-item").forEach((n) => n.addEventListener("click", () => switchPage(n.dataset.page)));
  // Menu trên màn hình hẹp: mở bằng ☰; đóng bằng ✕, bấm ra ngoài, phím Esc hoặc chọn một trang.
  $("#menu-btn").onclick = () => setMenu(!$("#sidebar").classList.contains("open"));
  $("#sidebar-close").onclick = () => setMenu(false);
  $("#sidebar-backdrop").onclick = () => setMenu(false);
  document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") setMenu(false); });
  try {
    [S.results, S.facts, S.metrics, S.examples] = await Promise.all([
      getJSON("data/results.json"), getJSON("data/facts.json"),
      getJSON("data/metrics.json"), getJSON("data/examples.json"),
    ]);
  } catch (err) {
    document.querySelector(".page-content").insertAdjacentHTML("afterbegin",
      `<div class="notice-banner"><strong>Không đọc được dữ liệu (${esc(err.message)}).</strong> Hãy mở trang qua HTTP server (run_demo.bat), không mở trực tiếp tệp index.html.</div>`);
    return;
  }
  renderOverview();
  renderCompanies();
  setupReportPage();
  renderCheck();
  renderEvaluation();
  renderQuantum();
  switchPage(location.hash.slice(1) || "overview");
  window.addEventListener("hashchange", () => switchPage(location.hash.slice(1)));
}

document.addEventListener("DOMContentLoaded", init);
