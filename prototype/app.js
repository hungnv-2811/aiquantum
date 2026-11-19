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

const S = { results: [], facts: {}, metrics: null, examples: [], charts: {} };

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
  $("#breadcrumb-page").textContent = PAGES[page];
  $("#sidebar").classList.remove("open");
  if (location.hash !== `#${page}`) history.replaceState(null, "", `#${page}`);
  if (page === "check") ensurePy().catch(() => {});
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
  const score = c.score == null ? "" : ` · điểm ${nf(c.score, 2)}`;
  return `<div class="claim ${v.cls}">
    <div class="claim-top">${badge(c.verdict)} ${where}${esc(metricVi(c.metric))}${c.page ? ` · BCTN trang ${c.page}` : " · câu nhập tay"}${score}</div>
    <div class="claim-quote">“${esc(c.text)}”</div>
    ${(c.evidence || []).map(evidenceHTML).join("")}
  </div>`;
}

/* ── Tổng quan ── */
function renderOverview() {
  const p = S.metrics.pipeline;
  const now = p.verdicts_now, before = p.verdicts_before;
  const kpis = [
    ["Doanh nghiệp", p.companies, "13 phi ngân hàng + 3 ngân hàng (ngoài phạm vi)", "indigo", "🏢"],
    ["Báo cáo đã đối chiếu", p.reports, "cặp BCTN ↔ BCTC kiểm toán", "cyan", "📄"],
    ["Khẳng định trích được", nf(p.claims_now), `trước khi vá nền: ${nf(p.claims_before)}`, "purple", "🔎"],
    ["Nhất quán", nf(now["nhất quán"]), "khớp số liệu BCTC", "emerald", "✓"],
    ["Cần xem xét", nf(now["mâu thuẫn"]), `trước khi vá nền: ${nf(before["mâu thuẫn"])}`, "amber", "!"],
    ["Chưa kiểm chứng được", nf(now["không kiểm chứng được"]), "im lặng có lý do", "rose", "?"],
  ];
  $("#kpi-grid").innerHTML = kpis.map(([label, value, sub, color, icon]) => `
    <div class="kpi-card"><div class="kpi-header"><div class="kpi-label">${label}</div><div class="kpi-icon ${color}">${icon}</div></div>
    <div class="kpi-value">${value}</div><div class="kpi-change neutral">${sub}</div></div>`).join("");

  const labels = ["Nhất quán", "Cần xem xét", "Chưa kiểm chứng được"];
  const keys = ["nhất quán", "mâu thuẫn", "không kiểm chứng được"];
  drawChart("chart-before-after", {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: `Bản 21/09 (${nf(p.claims_before)} khẳng định)`, data: keys.map((k) => before[k]), backgroundColor: "rgba(148,163,184,0.45)" },
        { label: `Sau vá nền 19/11 (${nf(p.claims_now)} khẳng định)`, data: keys.map((k) => now[k]), backgroundColor: ["#10b981", "#f59e0b", "#64748b"] },
      ],
    },
    options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } },
  });
  $("#before-after-note").innerHTML =
    `Rà soát bản 21/09 cho thấy gần hết ${before["mâu thuẫn"]} cờ là cáo buộc oan (câu về công ty con, rác bố cục, câu không phải kết quả, sai đơn vị tính…). ` +
    `Sau khi vá đúng các nguyên nhân đó còn <b>${now["mâu thuẫn"]}</b> câu cần xem xét. Số khẳng định giảm vì hệ thống lọc bỏ câu không đối chiếu được, thay vì đoán.`;

  const flagged = [];
  for (const r of S.results) for (const c of r.claims) if (c.verdict === "mâu thuẫn") flagged.push([r, c]);
  const ev = S.metrics.evaluation;
  const caveat = ev
    ? `<div class="notice-banner"><strong>Đọc danh sách này một cách thận trọng.</strong> Khi gán nhãn mù ${ev.after.flags_in_sample} câu trong nhóm này,
       <b>${ev.after.true_mt}</b> câu được xác nhận là mâu thuẫn thật; phần lớn còn lại là câu nói về một mảng/công ty con hoặc mảnh bố cục mà hệ thống chưa lọc được
       (xem trang Đánh giá chất lượng). Nhóm này là danh sách để người xem lại, không phải danh sách sai phạm.</div>`
    : "";
  $("#review-list").innerHTML = caveat + (flagged.length
    ? flagged.map(([r, c]) => claimHTML(c, r)).join("")
    : `<div class="empty-state"><p>Không có câu nào cần xem xét.</p></div>`);
}

/* ── Doanh nghiệp: bảng nhiệt ── */
function scoreColor(s) {
  if (s == null) return "transparent";
  const hue = Math.round(30 + 110 * s); // 30 = cam, 140 = xanh
  return `hsla(${hue}, 70%, 45%, 0.28)`;
}

function renderCompanies() {
  const years = [...new Set(S.results.map((r) => r.year))].sort();
  const tickers = [...new Set(S.results.map((r) => r.ticker))].sort();
  const byKey = Object.fromEntries(S.results.map((r) => [`${r.ticker}_${r.year}`, r]));
  let html = `<thead><tr><th>Doanh nghiệp</th>${years.map((y) => `<th>${y}</th>`).join("")}</tr></thead><tbody>`;
  for (const t of tickers) {
    const any = S.results.find((r) => r.ticker === t);
    html += `<tr><td><b>${t}</b> <span class="note">${esc(any.sector)}${any.bank ? " · ngoài phạm vi (TT49)" : ""}</span></td>`;
    for (const y of years) {
      const r = byKey[`${t}_${y}`];
      if (!r) { html += `<td></td>`; continue; }
      const n = r.counts;
      html += `<td class="cell" data-t="${t}" data-y="${y}" style="background:${scoreColor(r.score)}">
        ${r.score == null ? "—" : nf(r.score, 2)}<span class="sub">${n["nhất quán"]}✓ ${n["mâu thuẫn"]}! ${n["không kiểm chứng được"]}?</span></td>`;
    }
    html += `</tr>`;
  }
  $("#heat-table").innerHTML = html + "</tbody>";
  $("#heat-table").onclick = (ev) => {
    const td = ev.target.closest("td.cell");
    if (!td) return;
    openReport(td.dataset.t, Number(td.dataset.y));
  };
}

/* ── Chi tiết báo cáo ── */
let reportFilter = "all";

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
  const r = S.results.find((x) => x.ticker === $("#report-ticker").value && x.year === Number($("#report-year").value));
  if (!r) return;
  const src = S.facts[`${r.ticker}_${r.year}`]?.source || "";
  $("#report-summary").innerHTML = `<p class="note">${r.ticker} ${r.year} · ${esc(r.sector)} · điểm NNC <b>${r.score == null ? "—" : nf(r.score, 2)}</b> ·
    ${r.counts["nhất quán"]} nhất quán · ${r.counts["mâu thuẫn"]} cần xem xét · ${r.counts["không kiểm chứng được"]} chưa kiểm chứng được<br>
    Số liệu đối chiếu: <code>${esc(src)}</code>${r.bank ? " · <b>Ngân hàng lập BCTC theo Thông tư 49 — ngoài phạm vi</b>" : ""}</p>`;
  const claims = r.claims.filter((c) => reportFilter === "all" || c.verdict === reportFilter);
  $("#report-claims").innerHTML = claims.length ? claims.map((c) => claimHTML(c)).join("")
    : `<div class="empty-state"><p>Không có khẳng định nào trong nhóm này.</p></div>`;
}

function openReport(ticker, year) {
  $("#report-ticker").value = ticker;
  $("#report-ticker").onchange();
  $("#report-year").value = String(year);
  renderReport();
  switchPage("report");
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

function pyStatus(cls, text) {
  const el = $("#py-status");
  el.className = `py-status ${cls}`;
  el.textContent = text;
}

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
  pyStatus("busy", "Đang tải Pyodide (lần đầu ~10 MB)…");
  pyLoading = (async () => {
    try {
      if (!window.loadPyodide) await loadScript(PYODIDE_URL + "pyodide.js");
      const p = await window.loadPyodide({ indexURL: PYODIDE_URL });
      pyStatus("busy", "Đang nạp mã nguồn SmartAudit…");
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
      pyStatus("ready", "✓ Lõi Python đã sẵn sàng");
      return p;
    } catch (err) {
      pyLoading = null;
      pyStatus("err", `Không nạp được lõi Python: ${err.message}. Cần kết nối mạng tới cdn.jsdelivr.net.`);
      throw err;
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
    box.innerHTML = `<p class="note">Đối chiếu với ${esc(S.facts[key]?.source || key)}</p>` +
      out.map((c) => claimHTML(c)).join("");
  } catch (err) {
    box.innerHTML = `<div class="empty-state"><p>${esc(err.message)}</p></div>`;
  }
}

function renderCheck() {
  fillTickerYear($("#check-ticker"), $("#check-year"), Object.keys(S.facts), () => {});
  $("#check-run").onclick = runCheck;
  $("#examples").innerHTML = `<div class="lbl">Thử nhanh</div>` + S.examples.map((e, i) => `
    <button class="example" data-i="${i}"><span class="tag ${e.kind.includes("chủ đích") ? "synthetic" : ""}">${esc(e.kind)} · ${e.ticker} ${e.year}</span>${esc(e.text)}</button>`).join("");
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

/* ── Đánh giá ── */
function renderEvaluation() {
  const inj = S.metrics.injected;
  const ev = S.metrics.evaluation;
  const kpis = [];
  if (inj) {
    kpis.push(["Recall trên tập chèn lỗi", pct(inj.recall_chen_loi.ty_le), `${inj.recall_chen_loi.dung}/${inj.recall_chen_loi.n} câu bị sửa sai được bắt — dữ liệu tổng hợp`, "emerald", "🎯"]);
    kpis.push(["Báo động giả trên đối chứng", `${inj.bao_dong_gia_doi_chung.n - inj.bao_dong_gia_doi_chung.dung}/${inj.bao_dong_gia_doi_chung.n}`, "câu gốc và câu lệch 0,5% (trong dung sai)", "cyan", "🛡"]);
  }
  if (ev) {
    kpis.push(["Precision “cần xem xét” (sau vá)", ev.after?.precision == null ? "—" : pct(ev.after.precision, 0),
      `${ev.after?.true_mt ?? "—"}/${ev.after?.flags_in_sample ?? "—"} cờ trong mẫu là mâu thuẫn thật · nhãn bạc`, "amber", "!"]);
    kpis.push(["Đồng thuận 2 người gán", ev.kappa_nhan == null ? "—" : nf(ev.kappa_nhan, 2), "Cohen's kappa trên nhãn phán quyết", "purple", "κ"]);
  }
  $("#eval-kpis").innerHTML = kpis.map(([label, value, sub, color, icon]) => `
    <div class="kpi-card"><div class="kpi-header"><div class="kpi-label">${label}</div><div class="kpi-icon ${color}">${icon}</div></div>
    <div class="kpi-value">${value}</div><div class="kpi-change neutral">${sub}</div></div>`).join("");

  if (inj) {
    const names = { gia_tri: "Đổi giá trị (±2–20%)", phan_tram: "Đổi tỷ lệ % (+2–10 điểm)", huong: "Đảo hướng tăng/giảm", kiem_soat_chi_phi: "“Kiểm soát chi phí” khi tỷ lệ chi phí tăng" };
    const ks = Object.keys(names).filter((k) => inj.recall_theo_loai[k]?.n);
    drawChart("chart-injected", {
      type: "bar",
      data: { labels: ks.map((k) => `${names[k]} (n=${inj.recall_theo_loai[k].n})`),
        datasets: [{ label: "Tỷ lệ phát hiện", data: ks.map((k) => inj.recall_theo_loai[k].ty_le * 100), backgroundColor: "#06b6d4" }] },
      options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 100, ticks: { callback: (v) => v + "%" } } } },
    });
  }

  if (!ev) {
    $("#eval-real").innerHTML = `<p class="note">Chưa có kết quả gán nhãn.</p>`;
  } else {
    const row = (name, b, a) => `<tr><td>${name}</td><td class="num">${b}</td><td class="num">${a}</td></tr>`;
    const ci = (x) => (x?.ci ? ` <span class="note">(KTC 95%: ${pct(x.ci[0], 0)}–${pct(x.ci[1], 0)})</span>` : "");
    $("#eval-real").innerHTML = `
      <table class="simple"><thead><tr><th></th><th>Bản 21/09</th><th>Sau vá 19/11</th></tr></thead><tbody>
      ${row("Số cờ “cần xem xét” trong mẫu", nf(ev.before.flags_in_sample), nf(ev.after.flags_in_sample))}
      ${row("… trong đó mâu thuẫn thật (theo nhãn)", nf(ev.before.true_mt), nf(ev.after.true_mt))}
      ${row("Precision", pct(ev.before.precision, 0) + ci(ev.before), pct(ev.after.precision, 0) + ci(ev.after))}
      ${row("Cờ oan ước tính trên toàn bộ khẳng định", nf(ev.before.false_flags_est), nf(ev.after.false_flags_est))}
      ${row("Mâu thuẫn thật trong mẫu bị gắn cờ", `${ev.gold_mt.flagged_before}/${ev.gold_mt.n}`, `${ev.gold_mt.flagged_after}/${ev.gold_mt.n}`)}
      </tbody></table>
      <p class="note">Hai người gán (tác tử AI, mù, độc lập) đồng thuận ${pct(ev.dong_thuan_nhan, 0)} · Cohen's kappa ${nf(ev.kappa_nhan, 2)}.
        Nhãn cuối: ${Object.entries(ev.gold_distribution).map(([k, v]) => `${k} ${v}`).join(" · ")}.</p>
      <p class="note"><b>Đọc kết quả:</b> mâu thuẫn thật rất hiếm (${ev.gold_mt.n}/${ev.n_labeled} câu trong mẫu) và đều là lỗi trình bày ở tỷ số, cơ cấu
        (hệ số nợ/VCSH, tỷ trọng tài sản) — loại mà bộ đối chiếu hiện chưa tính. Bản cũ “bắt” được ${ev.gold_mt.flagged_before} ca là do so nhầm tỷ số với khoản mục tiền;
        bản vá chặn phép so nhầm đó nên giảm mạnh cờ oan nhưng cũng mất các ca này. Bước tiếp theo: thêm phép tính tỷ số cơ cấu.</p>
      <p class="note">${esc(ev.ghi_chu || "")}</p>`;
  }
  const limits = [
    "Nhãn 300 cặp do <b>hai tác tử AI gán mù, độc lập</b> theo hướng dẫn của đội rồi phân xử bất đồng (nhãn bạc) — chưa được chuyên gia kiểm toán kiểm lại toàn bộ.",
    "Các bản vá nền dựa trên phân tích lỗi của chính 141 cờ bản 21/09, nên số đo “sau vá” trên mẫu này có thiên lệch lạc quan.",
    "Tập chèn lỗi là dữ liệu tổng hợp: đo độ nhạy của bộ đối chiếu, không đo tần suất mâu thuẫn ngoài thực tế.",
    "Chấp nhận 3 định nghĩa “doanh thu” (Mã 10, Mã 01, Mã 10 + 21 + 31) giảm cờ oan nhưng làm lọt một số câu bị sửa lệch nhỏ.",
    "Ngân hàng (Thông tư 49) và 15 báo cáo thường niên bản scan chưa được xử lý.",
  ];
  $("#eval-limits").innerHTML = `<ul class="prose" style="padding-left:18px">${limits.map((l) => `<li class="note" style="margin-bottom:6px">${l}</li>`).join("")}</ul>`;
}

/* ── Lượng tử ── */
function renderQuantum() {
  const q = S.metrics.quantum;
  if (!q) { $("#qka-text").innerHTML = `<p class="note">Chưa có kết quả.</p>`; return; }
  const order = [
    ["rapidfuzz_top8", "rapidfuzz (hệ thống đang dùng)"],
    ["svm_rbf", "SVM-RBF cổ điển"],
    ["qsvm_fixed", "QSVM — kernel ZZ cố định"],
    ["qsvm_qka", "QSVM + QKA (kernel học được)"],
  ].filter(([k]) => q.methods[k]);
  drawChart("chart-qka", {
    type: "bar",
    data: { labels: order.map(([, n]) => n),
      datasets: [{ label: "Accuracy (TB 5 phần)", data: order.map(([k]) => q.methods[k].accuracy_mean * 100),
        backgroundColor: order.map(([k]) => (k.startsWith("qsvm") ? "#8b5cf6" : "#06b6d4")) }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { min: 50, max: 100, ticks: { callback: (v) => v + "%" } } } },
  });
  const best = order.reduce((a, b) => (q.methods[b[0]].accuracy_mean > q.methods[a[0]].accuracy_mean ? b : a))[0];
  $("#qka-text").innerHTML = `
    <table class="simple"><thead><tr><th>Phương pháp</th><th>Accuracy</th><th>Macro-F1</th><th>Huấn luyện</th></tr></thead><tbody>
    ${order.map(([k, n]) => { const m = q.methods[k]; return `<tr class="${k === best ? "best" : ""}"><td>${n}</td>
      <td class="num">${nf(m.accuracy_mean, 3)} ± ${nf(m.accuracy_std, 3)}</td><td class="num">${nf(m.macro_f1_mean, 3)}</td>
      <td class="num">${nf(m.train_seconds_mean, 1)} s</td></tr>`; }).join("")}
    </tbody></table>
    <div class="prose" style="margin-top:12px">
      <p><b>Kết quả trung thực: lượng tử thua cổ điển ở quy mô này.</b> QKA học được kernel tốt hơn hẳn kernel cố định
        (kernel alignment trên tập huấn luyện ${nf(q.alignment?.qka_train_before?.mean, 3)} → ${nf(q.alignment?.qka_train_after?.mean, 3)}), nhưng vẫn thua SVM-RBF và huấn luyện chậm hơn hàng trăm lần.</p>
      <p>${q.n_qubits} qubit, mô phỏng statevector, ${q.n_folds} phần kiểm chứng chéo, ${nf(q.dataset?.n_samples)} tên khoản mục khác nhau, chạy ${nf((q.total_seconds || 0) / 60, 1)} phút.
        8 qubit vẫn mô phỏng được trên máy thường, nên ở cỡ này không thể có lợi thế lượng tử — đây là <b>kiểm chứng khả thi kỹ thuật</b>, không phải tuyên bố lợi thế.</p>
      <p>Lớp lượng tử <b>tháo rời được</b>: hệ thống chạy đầy đủ với kernel cổ điển. Phát hiện phụ: SVM cổ điển khớp tên khoản mục tốt hơn rapidfuzz mà hệ thống đang dùng.</p>
    </div>`;
}

/* ── Biểu đồ ── */
function drawChart(id, cfg) {
  if (S.charts[id]) S.charts[id].destroy();
  cfg.options = Object.assign({ responsive: true, maintainAspectRatio: false }, cfg.options || {});
  S.charts[id] = new Chart(document.getElementById(id), cfg);
}

/* ── Khởi động ── */
async function init() {
  if (window.Chart) {
    Chart.defaults.color = "#94a3b8";
    Chart.defaults.borderColor = "rgba(255,255,255,0.06)";
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
  }
  document.querySelectorAll(".nav-item").forEach((n) => n.addEventListener("click", () => switchPage(n.dataset.page)));
  $("#menu-btn").onclick = () => $("#sidebar").classList.toggle("open");
  document.querySelectorAll("#report-tabs .tab").forEach((t) => t.addEventListener("click", () => {
    document.querySelectorAll("#report-tabs .tab").forEach((x) => x.classList.toggle("active", x === t));
    reportFilter = t.dataset.filter;
    renderReport();
  }));
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
  $("#generated-at").textContent = `Dữ liệu xuất lúc ${S.metrics.generated_at.replace("T", " ")}`;
  renderOverview();
  renderCompanies();
  fillTickerYear($("#report-ticker"), $("#report-year"), S.results.map((r) => `${r.ticker}_${r.year}`), renderReport);
  renderReport();
  renderCheck();
  renderEvaluation();
  renderQuantum();
  switchPage(location.hash.slice(1) || "overview");
  window.addEventListener("hashchange", () => switchPage(location.hash.slice(1)));
}

document.addEventListener("DOMContentLoaded", init);
