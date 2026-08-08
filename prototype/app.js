// ============================================================
// SmartAudit-Quantum — Dashboard Application Logic
// Mã đội: AQ2026-064 | AI-Quantum Challenge 2026
// ============================================================

let currentPage = 'dashboard';
let selectedCompanyId = 'VNM';
let chartsInitialized = {};

// ── Page Navigation ──
function switchPage(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${page}`).classList.add('active');

  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
  if (navItem) navItem.classList.add('active');

  const titles = {
    dashboard: 'Dashboard',
    companies: 'Doanh nghiệp',
    analysis: 'Phân tích NNC',
    quantum: 'Quantum Engine',
    anomaly: 'Anomaly Detection',
    alerts: 'Cảnh báo'
  };
  const breadcrumbs = {
    dashboard: 'Tổng quan',
    companies: 'Danh sách DN',
    analysis: 'Chi tiết phân tích',
    quantum: 'Quantum Computing',
    anomaly: 'Phát hiện bất thường',
    alerts: 'Lịch sử cảnh báo'
  };

  document.getElementById('page-title').textContent = titles[page] || page;
  document.getElementById('breadcrumb-page').textContent = breadcrumbs[page] || page;

  // Initialize charts on first visit
  if (page === 'dashboard' && !chartsInitialized.dashboard) initDashboardCharts();
  if (page === 'quantum' && !chartsInitialized.quantum) initQuantumCharts();
  if (page === 'anomaly' && !chartsInitialized.anomaly) initAnomalyCharts();
  if (page === 'companies') renderCompanyTable();
  if (page === 'analysis') renderCompanyDetail();
  if (page === 'alerts') renderAllAlerts();
}

// ── KPI Cards ──
function renderKPIs() {
  const grid = document.getElementById('kpi-grid');
  const kpis = [
    { label: 'DN đã phân tích', value: MARKET_STATS.analyzedCompanies, icon: '🏢', iconClass: 'indigo', change: '+12', positive: true },
    { label: 'NNC Score TB', value: MARKET_STATS.avgConsistency + '%', icon: '📊', iconClass: 'cyan', change: '-1.2%', positive: false },
    { label: 'Bất thường phát hiện', value: MARKET_STATS.anomaliesDetected, icon: '🚨', iconClass: 'rose', change: '+3', positive: false },
    { label: 'Claims đã xác minh', value: MARKET_STATS.verifiedClaims.toLocaleString(), icon: '✓', iconClass: 'emerald', change: '+248', positive: true },
    { label: 'Claims bất nhất quán', value: MARKET_STATS.inconsistentClaims, icon: '⚠', iconClass: 'amber', change: '+18', positive: false },
    { label: 'Quantum Advantage', value: MARKET_STATS.quantumAdvantage, icon: '⚛', iconClass: 'purple', change: 'vs Classical', positive: true }
  ];

  grid.innerHTML = kpis.map(k => `
    <div class="kpi-card">
      <div class="kpi-header">
        <div class="kpi-label">${k.label}</div>
        <div class="kpi-icon ${k.iconClass}">${k.icon}</div>
      </div>
      <div class="kpi-value">${k.value}</div>
      <span class="kpi-change ${k.positive ? 'positive' : 'negative'}">${k.positive ? '↑' : '↓'} ${k.change}</span>
    </div>
  `).join('');
}

// ── Alert List ──
function renderAlerts() {
  const container = document.getElementById('alert-list');
  container.innerHTML = ALERTS.map(a => `
    <div class="alert-item">
      <div class="alert-dot ${a.type}"></div>
      <div class="alert-content">
        <div class="alert-meta">
          <span class="alert-time">${a.time}</span>
          <span class="alert-company">${a.company}</span>
        </div>
        <div class="alert-message">${a.message}</div>
      </div>
    </div>
  `).join('');
}

function renderAllAlerts() {
  const container = document.getElementById('all-alerts-list');
  const expandedAlerts = [
    ...ALERTS,
    { time: "13:30", company: "HPG", type: "info", message: "Phân tích BCTC 2024 hoàn tất. 3/5 claims nhất quán." },
    { time: "12:15", company: "SCB", type: "critical", message: "QSVM Anomaly Score = 0.95 — vượt ngưỡng cảnh báo (>0.7). Cần thanh tra ngay." },
    { time: "11:45", company: "MWG", type: "warning", message: "Sai lệch giữa thuyết minh phân khúc BHX và tuyên bố hòa vốn (NNC = 0.18)." },
    { time: "11:00", company: "FPT", type: "success", message: "Hoàn tất benchmark 5 năm (2020-2024). NNC avg = 0.95. Doanh nghiệp mẫu mực." },
    { time: "10:30", company: "VNM", type: "info", message: "Chi phí bán hàng: narrative nói 'giảm' nhưng thực tế tăng 6.2%. Đề xuất review lại MD&A." },
  ];
  container.innerHTML = expandedAlerts.map(a => `
    <div class="alert-item">
      <div class="alert-dot ${a.type}"></div>
      <div class="alert-content">
        <div class="alert-meta">
          <span class="alert-time">${a.time}</span>
          <span class="alert-company">${a.company}</span>
        </div>
        <div class="alert-message">${a.message}</div>
      </div>
    </div>
  `).join('');
}

function filterAlerts(type) {
  // Simple filter visual feedback
  const items = document.querySelectorAll('#all-alerts-list .alert-item');
  items.forEach(item => {
    const dot = item.querySelector('.alert-dot');
    if (type === 'all' || dot.classList.contains(type)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

// ── Company Table ──
function renderCompanyTable(filter) {
  const tbody = document.getElementById('company-table-body');
  let companies = COMPANIES;
  if (filter && filter !== 'all') {
    companies = companies.filter(c => c.sector === filter);
  }

  tbody.innerHTML = companies.map(c => {
    const latestScore = c.consistencyScores[c.consistencyScores.length - 1];
    const latestAnomaly = c.quantumAnomalyScores[c.quantumAnomalyScores.length - 1];
    const scoreClass = latestScore >= 85 ? 'high' : latestScore >= 70 ? 'medium' : 'low';
    const avatarColor = c.riskLevel === 'Rất cao' ? '#ef4444' : c.riskLevel === 'Trung bình' ? '#f59e0b' : '#22c55e';

    return `
      <tr onclick="goToAnalysis('${c.id}')">
        <td>
          <div class="company-name">
            <div class="company-avatar" style="background:${avatarColor}">${c.id}</div>
            <div>
              <div style="font-weight:600">${c.name}</div>
              <div style="font-size:11px;color:var(--text-muted)">${c.exchange}</div>
            </div>
          </div>
        </td>
        <td style="font-size:12px;color:var(--text-secondary)">${c.sector}</td>
        <td>
          <span class="score-badge ${scoreClass}">${latestScore}%</span>
        </td>
        <td>
          <div style="display:flex;align-items:center;gap:8px">
            <div style="flex:1">
              <div class="score-bar">
                <div class="score-bar-fill" style="width:${latestAnomaly*100}%; background:${latestAnomaly > 0.5 ? 'var(--accent-rose)' : latestAnomaly > 0.3 ? 'var(--accent-amber)' : 'var(--accent-emerald)'}"></div>
              </div>
            </div>
            <span style="font-size:12px;font-weight:600;font-family:'JetBrains Mono',monospace;color:${latestAnomaly > 0.5 ? 'var(--accent-rose)' : 'var(--text-secondary)'}">${latestAnomaly.toFixed(2)}</span>
          </div>
        </td>
        <td>
          <span class="risk-tag" style="background:${c.riskColor}22;color:${c.riskColor};border:1px solid ${c.riskColor}44">${c.riskLevel}</span>
        </td>
        <td style="font-size:13px;font-weight:600">${c.claims.length}</td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); goToAnalysis('${c.id}')">Xem →</button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterCompanies() {
  const filter = document.getElementById('sectorFilter').value;
  renderCompanyTable(filter);
}

function goToAnalysis(companyId) {
  selectedCompanyId = companyId;
  document.getElementById('companySelect').value = companyId;
  switchPage('analysis');
}

function handleSearch(value) {
  const v = value.toLowerCase().trim();
  if (!v) return;
  const found = COMPANIES.find(c => c.id.toLowerCase().includes(v) || c.name.toLowerCase().includes(v));
  if (found) {
    goToAnalysis(found.id);
  }
}

// ── Company Detail (Analysis Page) ──
function selectCompany(id) {
  selectedCompanyId = id;
  renderCompanyDetail();
}

function renderCompanyDetail() {
  const c = COMPANIES.find(co => co.id === selectedCompanyId);
  if (!c) return;

  const container = document.getElementById('company-detail-container');
  const latestScore = c.consistencyScores[c.consistencyScores.length - 1];
  const latestAnomaly = c.quantumAnomalyScores[c.quantumAnomalyScores.length - 1];

  container.innerHTML = `
    <div class="company-detail-header">
      <div class="company-detail-avatar" style="background:${c.riskColor}">${c.id}</div>
      <div class="company-detail-info">
        <h3>${c.name}</h3>
        <p>${c.sector} | ${c.exchange} | Mức rủi ro: <span style="color:${c.riskColor};font-weight:700">${c.riskLevel}</span></p>
      </div>
      <div class="company-detail-stats">
        <div class="detail-stat">
          <div class="detail-stat-value" style="color:${latestScore >= 85 ? 'var(--accent-emerald)' : latestScore >= 70 ? 'var(--accent-amber)' : 'var(--accent-rose)'}">${latestScore}%</div>
          <div class="detail-stat-label">NNC Score</div>
        </div>
        <div class="detail-stat">
          <div class="detail-stat-value" style="color:${latestAnomaly > 0.5 ? 'var(--accent-rose)' : 'var(--text-primary)'}">${latestAnomaly.toFixed(2)}</div>
          <div class="detail-stat-label">Q-Anomaly</div>
        </div>
        <div class="detail-stat">
          <div class="detail-stat-value">${c.claims.length}</div>
          <div class="detail-stat-label">Claims</div>
        </div>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:24px">
      <div class="card">
        <div class="card-header">
          <div class="card-title">📈 NNC Score & Anomaly theo năm</div>
        </div>
        <div class="card-body">
          <div class="chart-container small">
            <canvas id="companyTrendChart"></canvas>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <div class="card-title">💰 Doanh thu: Claimed vs Reported</div>
        </div>
        <div class="card-body">
          <div class="chart-container small">
            <canvas id="revenueCompareChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-title">🔍 Chi tiết Claim-Evidence (${c.claims.length} claims)</div>
        <div style="display:flex;gap:6px">
          <span class="score-badge high">✓ ${c.claims.filter(cl => cl.status === 'consistent').length} Nhất quán</span>
          <span class="score-badge low">✗ ${c.claims.filter(cl => cl.status === 'inconsistent').length} Bất nhất quán</span>
        </div>
      </div>
      <div class="card-body">
        ${c.claims.map(cl => `
          <div class="claim-card ${cl.status}">
            <div class="claim-header">
              <span class="claim-category">${cl.category}</span>
              <span class="claim-status ${cl.status}">${cl.status === 'consistent' ? '✓ Nhất quán' : '✗ Bất nhất quán'}</span>
            </div>
            <div class="claim-text">📝 <strong>Claim:</strong> "${cl.text}"</div>
            <div class="claim-evidence">📊 <strong>Evidence:</strong> ${cl.evidence}</div>
            <div class="claim-score">
              <span>NNC Score:</span>
              <div class="claim-score-bar">
                <div class="claim-score-bar-fill" style="width:${cl.nncScore * 100}%; background:${cl.nncScore >= 0.7 ? 'var(--accent-emerald)' : cl.nncScore >= 0.4 ? 'var(--accent-amber)' : 'var(--accent-rose)'}"></div>
              </div>
              <span style="font-family:'JetBrains Mono',monospace;font-weight:700;color:${cl.nncScore >= 0.7 ? 'var(--accent-emerald)' : cl.nncScore >= 0.4 ? 'var(--accent-amber)' : 'var(--accent-rose)'}">${cl.nncScore.toFixed(2)}</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  // Render company charts
  setTimeout(() => {
    renderCompanyTrendChart(c);
    renderRevenueCompareChart(c);
  }, 100);
}

function renderCompanyTrendChart(c) {
  const ctx = document.getElementById('companyTrendChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: c.years.map(String),
      datasets: [
        {
          label: 'NNC Score (%)',
          data: c.consistencyScores,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Quantum Anomaly',
          data: c.quantumAnomalyScores,
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244,63,94,0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { position: 'left', min: 0, max: 100, ticks: { color: '#6366f1' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y1: { position: 'right', min: 0, max: 1, ticks: { color: '#f43f5e' }, grid: { display: false } }
      }
    }
  });
}

function renderRevenueCompareChart(c) {
  const ctx = document.getElementById('revenueCompareChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: c.years.map(String),
      datasets: [
        {
          label: 'Số liệu thực (BCTC)',
          data: c.revenueReported,
          backgroundColor: 'rgba(99,102,241,0.6)',
          borderRadius: 4
        },
        {
          label: 'Narrative (MD&A)',
          data: c.revenueClaimed,
          backgroundColor: 'rgba(6,182,212,0.6)',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#64748b', callback: v => (v/1000).toFixed(0) + 'k' }, grid: { color: 'rgba(255,255,255,0.04)' } }
      }
    }
  });
}

function runAnalysis() {
  const c = COMPANIES.find(co => co.id === selectedCompanyId);
  if (!c) return;
  // Simulate analysis animation
  const btn = document.querySelector('#page-analysis .btn-primary');
  btn.textContent = '⏳ Đang phân tích...';
  btn.style.opacity = '0.7';
  setTimeout(() => {
    btn.textContent = '✓ Hoàn tất!';
    btn.style.opacity = '1';
    btn.style.background = 'var(--gradient-success)';
    setTimeout(() => {
      btn.textContent = '▶ Chạy phân tích';
      btn.style.background = '';
    }, 2000);
  }, 1500);
}

// ── Dashboard Charts ──
function initDashboardCharts() {
  chartsInitialized.dashboard = true;

  // Sector Chart
  const sectorCtx = document.getElementById('sectorChart');
  new Chart(sectorCtx, {
    type: 'bar',
    data: {
      labels: SECTOR_DATA.map(s => s.sector),
      datasets: [{
        label: 'NNC Score TB (%)',
        data: SECTOR_DATA.map(s => s.avgScore),
        backgroundColor: SECTOR_DATA.map(s => s.color + '99'),
        borderColor: SECTOR_DATA.map(s => s.color),
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            afterLabel: (ctx) => `Số DN: ${SECTOR_DATA[ctx.dataIndex].count}`
          }
        }
      },
      scales: {
        x: { min: 50, max: 100, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#94a3b8', font: { size: 12 } }, grid: { display: false } }
      }
    }
  });

  // Quantum vs Classical Comparison
  const qcCtx = document.getElementById('quantumCompareChart');
  new Chart(qcCtx, {
    type: 'radar',
    data: {
      labels: ['Retrieval Accuracy', 'Anomaly F1', 'NNC Precision', 'Processing Speed', 'Feature Capture', 'Noise Robustness'],
      datasets: [
        {
          label: 'Quantum-Enhanced',
          data: [94.2, 91.5, 89.3, 72, 96.1, 88.4],
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,0.15)',
          pointBackgroundColor: '#8b5cf6',
          pointBorderColor: '#fff',
          pointRadius: 4
        },
        {
          label: 'Classical Baseline',
          data: [82.1, 83.2, 84.7, 95, 78.5, 80.1],
          borderColor: '#64748b',
          backgroundColor: 'rgba(100,116,139,0.1)',
          pointBackgroundColor: '#64748b',
          pointBorderColor: '#fff',
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      scales: {
        r: {
          min: 50, max: 100,
          ticks: { color: '#64748b', backdropColor: 'transparent', font: { size: 10 } },
          grid: { color: 'rgba(255,255,255,0.06)' },
          pointLabels: { color: '#94a3b8', font: { size: 11 } },
          angleLines: { color: 'rgba(255,255,255,0.06)' }
        }
      }
    }
  });

  // NNC Distribution
  const nncCtx = document.getElementById('nncDistChart');
  const nncBins = [0, 0, 2, 5, 8, 12, 18, 28, 45, 38];
  new Chart(nncCtx, {
    type: 'bar',
    data: {
      labels: ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'],
      datasets: [{
        label: 'Số Claims',
        data: nncBins,
        backgroundColor: nncBins.map((_, i) => {
          if (i >= 7) return 'rgba(16,185,129,0.7)';
          if (i >= 4) return 'rgba(245,158,11,0.7)';
          return 'rgba(244,63,94,0.7)';
        }),
        borderRadius: 4,
        barPercentage: 0.85
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'NNC Score Range', color: '#64748b' } },
        y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'Số Claims', color: '#64748b' } }
      }
    }
  });
}

// ── Quantum Charts ──
function initQuantumCharts() {
  chartsInitialized.quantum = true;

  // Convergence Chart
  const convCtx = document.getElementById('convergenceChart');
  const data = QUANTUM_CIRCUIT.convergenceData;
  new Chart(convCtx, {
    type: 'line',
    data: {
      labels: data.map(d => d.iteration),
      datasets: [
        {
          label: 'QKA (Quantum)',
          data: data.map(d => d.kernelAlignment),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          borderWidth: 2
        },
        {
          label: 'Classical Baseline',
          data: data.map(d => d.classicalBaseline),
          borderColor: '#64748b',
          backgroundColor: 'rgba(100,116,139,0.05)',
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          borderWidth: 2,
          borderDash: [5, 5]
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#64748b', maxTicksLimit: 10 }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'SPSA Iterations', color: '#64748b' } },
        y: { min: 0.2, max: 1.0, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'Kernel Alignment', color: '#64748b' } }
      }
    }
  });

  // Quantum Circuit Visualization
  renderQuantumCircuit();

  // Kernel Heatmap (simulated as scatter/bubble)
  const hmCtx = document.getElementById('kernelHeatmap');
  const hmData = [];
  for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 8; j++) {
      const val = i === j ? 1.0 : Math.max(0.05, 0.8 * Math.exp(-0.5 * Math.pow(i - j, 2)) + (Math.random() - 0.5) * 0.15);
      hmData.push({ x: j, y: i, v: val });
    }
  }
  new Chart(hmCtx, {
    type: 'bubble',
    data: {
      datasets: [{
        label: 'K(xᵢ, xⱼ)',
        data: hmData.map(d => ({ x: d.x, y: d.y, r: d.v * 14 })),
        backgroundColor: hmData.map(d => {
          const intensity = Math.floor(d.v * 255);
          return `rgba(${139 - intensity * 0.3}, ${92 + intensity * 0.3}, ${246}, ${0.3 + d.v * 0.6})`;
        }),
        borderColor: 'transparent'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          min: -0.5, max: 7.5,
          ticks: { color: '#64748b', callback: v => `x${v}`, stepSize: 1 },
          grid: { color: 'rgba(255,255,255,0.04)' },
          title: { display: true, text: 'Sample Index j', color: '#64748b' }
        },
        y: {
          min: -0.5, max: 7.5,
          ticks: { color: '#64748b', callback: v => `x${v}`, stepSize: 1 },
          grid: { color: 'rgba(255,255,255,0.04)' },
          title: { display: true, text: 'Sample Index i', color: '#64748b' }
        }
      }
    }
  });
}

function renderQuantumCircuit() {
  const container = document.getElementById('quantum-circuit');
  const gateTypes = ['h', 'ry', 'cx', 'rz', 'wire', 'rx', 'cx', 'ry', 'wire', 'rz', 'h', 'cx'];
  const gateLabels = { h: 'H', ry: 'RY', rx: 'RX', rz: 'RZ', cx: 'CX', wire: '─' };

  let html = '';
  for (let q = 0; q < 8; q++) {
    html += `<div class="qubit-line"><span class="qubit-label">q${q}</span>`;
    for (let g = 0; g < 12; g++) {
      const type = gateTypes[(q + g) % gateTypes.length];
      html += `<span class="gate ${type}" title="${gateLabels[type]} gate on qubit ${q}">${gateLabels[type]}</span>`;
    }
    html += `<span style="color:var(--text-muted);margin-left:8px">→ |ψ⟩</span></div>`;
  }
  container.innerHTML = html;
}

// ── Anomaly Charts ──
function initAnomalyCharts() {
  chartsInitialized.anomaly = true;

  // Ranking
  renderAnomalyRanking();

  // Anomaly Time Chart
  const atCtx = document.getElementById('anomalyTimeChart');
  new Chart(atCtx, {
    type: 'line',
    data: {
      labels: ['2020', '2021', '2022', '2023', '2024'],
      datasets: COMPANIES.map(c => ({
        label: c.id,
        data: c.quantumAnomalyScores,
        borderColor: c.riskColor,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: c.riskColor,
        borderWidth: 2
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { min: 0, max: 1, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'Quantum Anomaly Score', color: '#64748b' } }
      }
    }
  });

  // Scatter Chart
  const scCtx = document.getElementById('scatterChart');
  new Chart(scCtx, {
    type: 'scatter',
    data: {
      datasets: COMPANIES.map(c => ({
        label: c.id,
        data: [{ x: c.consistencyScores[c.consistencyScores.length - 1], y: c.quantumAnomalyScores[c.quantumAnomalyScores.length - 1] }],
        backgroundColor: c.riskColor + 'cc',
        borderColor: c.riskColor,
        pointRadius: 10,
        pointHoverRadius: 14
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: NNC=${ctx.parsed.x}%, Anomaly=${ctx.parsed.y.toFixed(2)}`
          }
        }
      },
      scales: {
        x: { min: 0, max: 100, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'NNC Score (%)', color: '#64748b' } },
        y: { min: 0, max: 1, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' }, title: { display: true, text: 'Quantum Anomaly Score', color: '#64748b' } }
      }
    }
  });
}

function renderAnomalyRanking() {
  const container = document.getElementById('anomaly-ranking');
  const sorted = [...COMPANIES].sort((a, b) => b.quantumAnomalyScores[b.quantumAnomalyScores.length - 1] - a.quantumAnomalyScores[a.quantumAnomalyScores.length - 1]);

  container.innerHTML = sorted.map((c, i) => {
    const score = c.quantumAnomalyScores[c.quantumAnomalyScores.length - 1];
    const nncScore = c.consistencyScores[c.consistencyScores.length - 1];
    const barColor = score > 0.5 ? 'var(--accent-rose)' : score > 0.3 ? 'var(--accent-amber)' : 'var(--accent-emerald)';

    return `
      <div style="display:flex;align-items:center;gap:16px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.04);cursor:pointer" onclick="goToAnalysis('${c.id}')">
        <div style="width:28px;text-align:center;font-weight:800;font-size:16px;color:${i === 0 ? 'var(--accent-rose)' : 'var(--text-muted)'}">#${i + 1}</div>
        <div class="company-avatar" style="background:${c.riskColor};width:36px;height:36px;font-size:11px">${c.id}</div>
        <div style="flex:1">
          <div style="font-weight:600;font-size:13px;margin-bottom:4px">${c.name}</div>
          <div class="score-bar">
            <div class="score-bar-fill" style="width:${score * 100}%;background:${barColor}"></div>
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:800;color:${barColor}">${score.toFixed(2)}</div>
          <div style="font-size:10px;color:var(--text-muted)">NNC: ${nncScore}%</div>
        </div>
        <span class="risk-tag" style="background:${c.riskColor}22;color:${c.riskColor};border:1px solid ${c.riskColor}44">${c.riskLevel}</span>
      </div>
    `;
  }).join('');
}

// ── Populate Company Selector ──
function populateCompanySelect() {
  const select = document.getElementById('companySelect');
  select.innerHTML = COMPANIES.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  select.value = selectedCompanyId;
}

// ── Initialize ──
document.addEventListener('DOMContentLoaded', () => {
  renderKPIs();
  renderAlerts();
  populateCompanySelect();
  initDashboardCharts();
});
