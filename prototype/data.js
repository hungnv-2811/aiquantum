// ============================================================
// SmartAudit-Quantum — Mock Data for MVP Prototype
// Mã đội: AQ2026-064 | AI-Quantum Challenge 2026
// ============================================================

const COMPANIES = [
  {
    id: "VNM",
    name: "Vinamilk (VNM)",
    sector: "Thực phẩm & Đồ uống",
    exchange: "HOSE",
    years: [2020, 2021, 2022, 2023, 2024],
    consistencyScores: [92, 89, 91, 87, 85],
    quantumAnomalyScores: [0.08, 0.12, 0.09, 0.18, 0.22],
    revenueReported: [59637, 60919, 59960, 58485, 62100],
    revenueClaimed: [59637, 60919, 60200, 58485, 62500],
    profitReported: [10581, 8529, 8578, 8344, 8920],
    profitClaimed: [10581, 8529, 8700, 8344, 9100],
    riskLevel: "Thấp",
    riskColor: "#22c55e",
    claims: [
      {
        id: 1,
        text: "Doanh thu thuần năm 2024 đạt 62.100 tỷ đồng, tăng 6,2% so với năm trước.",
        evidence: "BCKQKD: Doanh thu thuần = 62.100 tỷ VND (2024) vs 58.485 tỷ VND (2023) → Tăng trưởng = 6,18%",
        status: "consistent",
        nncScore: 0.96,
        category: "Doanh thu"
      },
      {
        id: 2,
        text: "Biên lợi nhuận gộp duy trì ở mức ổn định trên 42%.",
        evidence: "BCKQKD: LNG/DTT = 26.082/62.100 = 42,0% (2024). Năm 2023: 41,8%. Năm 2022: 39,2%.",
        status: "consistent",
        nncScore: 0.91,
        category: "Lợi nhuận"
      },
      {
        id: 3,
        text: "Chi phí bán hàng được kiểm soát tốt, giảm so với năm trước.",
        evidence: "BCKQKD: CPBH = 11.178 tỷ (2024) vs 10.523 tỷ (2023) → Tăng 6,2%, KHÔNG giảm.",
        status: "inconsistent",
        nncScore: 0.31,
        category: "Chi phí"
      },
      {
        id: 4,
        text: "Lợi nhuận sau thuế đạt mức tăng trưởng dương.",
        evidence: "BCKQKD: LNST = 8.920 tỷ (2024) vs 8.344 tỷ (2023) → Tăng 6,9%.",
        status: "consistent",
        nncScore: 0.94,
        category: "Lợi nhuận"
      }
    ]
  },
  {
    id: "HPG",
    name: "Hòa Phát (HPG)",
    sector: "Thép & Vật liệu",
    exchange: "HOSE",
    years: [2020, 2021, 2022, 2023, 2024],
    consistencyScores: [88, 82, 75, 71, 68],
    quantumAnomalyScores: [0.15, 0.25, 0.38, 0.42, 0.55],
    revenueReported: [91279, 150585, 141338, 120586, 142000],
    revenueClaimed: [91279, 150585, 143000, 122000, 145000],
    profitReported: [13506, 34520, 8289, 6800, 14200],
    profitClaimed: [13506, 34520, 8500, 7200, 15000],
    riskLevel: "Trung bình",
    riskColor: "#f59e0b",
    claims: [
      {
        id: 1,
        text: "Doanh thu năm 2024 tăng trưởng mạnh 17,8% nhờ sản lượng thép xây dựng phục hồi.",
        evidence: "BCKQKD: DTT = 142.000 tỷ (2024) vs 120.586 tỷ (2023) → Tăng 17,8%. Sản lượng thép XD tăng 22%.",
        status: "consistent",
        nncScore: 0.93,
        category: "Doanh thu"
      },
      {
        id: 2,
        text: "Biên lợi nhuận gộp cải thiện đáng kể lên mức 18%.",
        evidence: "BCKQKD: LNG/DTT = 22.720/142.000 = 16,0%. Con số 18% KHÔNG khớp.",
        status: "inconsistent",
        nncScore: 0.28,
        category: "Lợi nhuận"
      },
      {
        id: 3,
        text: "Tỷ lệ nợ vay trên vốn chủ sở hữu (D/E) được duy trì ở mức an toàn dưới 1,0 lần.",
        evidence: "BCĐKT: Nợ vay = 48.500 tỷ, VCSH = 72.300 tỷ → D/E = 0,67. Khớp.",
        status: "consistent",
        nncScore: 0.89,
        category: "Cấu trúc vốn"
      },
      {
        id: 4,
        text: "Chi phí tài chính giảm mạnh so với giai đoạn 2022-2023 nhờ lãi suất hạ.",
        evidence: "BCKQKD: CPTC 2024 = 4.100 tỷ vs 2023 = 5.890 tỷ → Giảm 30,4%. Giảm mạnh, KHỚP.",
        status: "consistent",
        nncScore: 0.92,
        category: "Chi phí"
      },
      {
        id: 5,
        text: "Dòng tiền hoạt động kinh doanh dương và tăng trưởng ổn định.",
        evidence: "BCLCTT: CFO 2024 = 8.200 tỷ (dương). CFO 2023 = -2.100 tỷ (ÂM). 'Ổn định' là KHÔNG CHÍNH XÁC vì 2023 âm.",
        status: "inconsistent",
        nncScore: 0.22,
        category: "Dòng tiền"
      }
    ]
  },
  {
    id: "FPT",
    name: "FPT Corporation (FPT)",
    sector: "Công nghệ Thông tin",
    exchange: "HOSE",
    years: [2020, 2021, 2022, 2023, 2024],
    consistencyScores: [95, 94, 93, 96, 97],
    quantumAnomalyScores: [0.05, 0.06, 0.07, 0.04, 0.03],
    revenueReported: [29830, 35657, 44010, 52618, 64847],
    revenueClaimed: [29830, 35657, 44010, 52618, 64847],
    profitReported: [4425, 5738, 6788, 8198, 10450],
    profitClaimed: [4425, 5738, 6788, 8198, 10450],
    riskLevel: "Rất thấp",
    riskColor: "#10b981",
    claims: [
      {
        id: 1,
        text: "Doanh thu năm 2024 đạt 64.847 tỷ đồng, tăng trưởng 23,2% YoY.",
        evidence: "BCKQKD: DTT = 64.847 tỷ (2024) vs 52.618 tỷ (2023) → Tăng 23,2%. KHỚP HOÀN TOÀN.",
        status: "consistent",
        nncScore: 0.99,
        category: "Doanh thu"
      },
      {
        id: 2,
        text: "Mảng Chuyển đổi số toàn cầu đóng góp 55% tổng doanh thu.",
        evidence: "Thuyết minh: DT mảng CĐS = 35.666 tỷ / 64.847 tỷ = 55,0%. KHỚP.",
        status: "consistent",
        nncScore: 0.98,
        category: "Doanh thu"
      },
      {
        id: 3,
        text: "LNST đạt trên 10.000 tỷ đồng, tăng trưởng 27,5%.",
        evidence: "BCKQKD: LNST = 10.450 tỷ. Tăng trưởng = (10.450-8.198)/8.198 = 27,5%. KHỚP.",
        status: "consistent",
        nncScore: 0.99,
        category: "Lợi nhuận"
      }
    ]
  },
  {
    id: "SCB",
    name: "SCB Fraud Case (Mô phỏng)",
    sector: "Ngân hàng",
    exchange: "HOSE",
    years: [2018, 2019, 2020, 2021, 2022],
    consistencyScores: [72, 58, 45, 32, 18],
    quantumAnomalyScores: [0.35, 0.55, 0.72, 0.88, 0.95],
    revenueReported: [12500, 14200, 15800, 18500, 21000],
    revenueClaimed: [12500, 16000, 19500, 25000, 35000],
    profitReported: [850, 920, 1050, 1200, 1400],
    profitClaimed: [850, 1500, 2200, 3500, 5000],
    riskLevel: "Rất cao",
    riskColor: "#ef4444",
    claims: [
      {
        id: 1,
        text: "Tổng tài sản tăng trưởng lành mạnh 25% so với năm trước.",
        evidence: "BCĐKT: Tổng TS = 761.000 tỷ (2022). Tuy nhiên, 93% tín dụng tập trung vào nhóm Vạn Thịnh Phát. 'Lành mạnh' là SAI.",
        status: "inconsistent",
        nncScore: 0.08,
        category: "Tổng tài sản"
      },
      {
        id: 2,
        text: "Tỷ lệ nợ xấu được kiểm soát tốt ở mức 1,5%.",
        evidence: "Thuyết minh: NPL ratio công bố = 1,5%. Tuy nhiên trái phiếu Vạn Thịnh Phát = 500.000 tỷ không được phân loại nợ xấu. NPL thực tế ước tính > 50%.",
        status: "inconsistent",
        nncScore: 0.05,
        category: "Nợ xấu"
      },
      {
        id: 3,
        text: "Lợi nhuận trước thuế đạt kết quả tích cực, tăng 16,7%.",
        evidence: "BCKQKD: LNTT = 1.400 tỷ (2022). Nhưng dự phòng rủi ro tín dụng bị che giấu. Sau thanh tra NHNN: lỗ lũy kế > 400.000 tỷ.",
        status: "inconsistent",
        nncScore: 0.03,
        category: "Lợi nhuận"
      },
      {
        id: 4,
        text: "Hệ số CAR đạt trên 8% theo quy định Basel II.",
        evidence: "Báo cáo CAR = 8,2%. Tuy nhiên, vốn tự có bị thổi phồng do 'loans' cho Vạn Thịnh Phát không bị trừ. CAR thực tế < 0%.",
        status: "inconsistent",
        nncScore: 0.02,
        category: "An toàn vốn"
      }
    ]
  },
  {
    id: "MWG",
    name: "Thế Giới Di Động (MWG)",
    sector: "Bán lẻ",
    exchange: "HOSE",
    years: [2020, 2021, 2022, 2023, 2024],
    consistencyScores: [90, 88, 80, 74, 82],
    quantumAnomalyScores: [0.10, 0.14, 0.28, 0.35, 0.20],
    revenueReported: [108500, 128600, 133000, 112200, 125000],
    revenueClaimed: [108500, 128600, 135000, 115000, 126000],
    profitReported: [3920, 4900, 4100, 810, 2800],
    profitClaimed: [3920, 4900, 4300, 850, 3000],
    riskLevel: "Trung bình",
    riskColor: "#f59e0b",
    claims: [
      {
        id: 1,
        text: "Năm 2024 đánh dấu sự phục hồi mạnh mẽ với doanh thu tăng 11,4%.",
        evidence: "BCKQKD: DTT = 125.000 tỷ (2024) vs 112.200 tỷ (2023) → Tăng 11,4%. KHỚP.",
        status: "consistent",
        nncScore: 0.95,
        category: "Doanh thu"
      },
      {
        id: 2,
        text: "Chuỗi Bách Hóa Xanh đã đạt điểm hòa vốn trong năm 2024.",
        evidence: "Thuyết minh phân khúc: BHX LN = -120 tỷ (2024). Chưa hòa vốn. KHÔNG KHỚP.",
        status: "inconsistent",
        nncScore: 0.18,
        category: "Lợi nhuận"
      },
      {
        id: 3,
        text: "LNST phục hồi gấp 3,5 lần so với năm 2023.",
        evidence: "BCKQKD: LNST = 2.800 tỷ (2024) vs 810 tỷ (2023) → Tăng 3,46 lần. KHỚP.",
        status: "consistent",
        nncScore: 0.97,
        category: "Lợi nhuận"
      }
    ]
  }
];

// Quantum circuit simulation data
const QUANTUM_CIRCUIT = {
  qubits: 8,
  depth: 12,
  gates: ["H", "CNOT", "RZ", "RY", "RX", "CZ"],
  featureMap: "ZZFeatureMap",
  optimizer: "SPSA",
  iterations: 150,
  convergenceData: Array.from({length: 150}, (_, i) => ({
    iteration: i + 1,
    kernelAlignment: Math.min(0.95, 0.3 + 0.65 * (1 - Math.exp(-i / 30)) + (Math.random() - 0.5) * 0.03),
    classicalBaseline: Math.min(0.82, 0.3 + 0.52 * (1 - Math.exp(-i / 25)) + (Math.random() - 0.5) * 0.02)
  }))
};

// Market overview statistics
const MARKET_STATS = {
  totalCompanies: 702,
  analyzedCompanies: 156,
  avgConsistency: 78.4,
  anomaliesDetected: 23,
  highRiskCompanies: 8,
  totalClaims: 4218,
  verifiedClaims: 3892,
  inconsistentClaims: 326,
  quantumAdvantage: "+12.7%",
  processingTime: "3.2s/report"
};

// Sector consistency data
const SECTOR_DATA = [
  { sector: "Ngân hàng", avgScore: 74, count: 27, color: "#6366f1" },
  { sector: "Bất động sản", avgScore: 68, count: 35, color: "#ec4899" },
  { sector: "Thép & VL XD", avgScore: 72, count: 18, color: "#f59e0b" },
  { sector: "Thực phẩm", avgScore: 86, count: 22, color: "#22c55e" },
  { sector: "Công nghệ", avgScore: 91, count: 12, color: "#06b6d4" },
  { sector: "Bán lẻ", avgScore: 79, count: 15, color: "#8b5cf6" },
  { sector: "Dược phẩm", avgScore: 83, count: 14, color: "#14b8a6" },
  { sector: "Năng lượng", avgScore: 71, count: 13, color: "#f97316" }
];

// Timeline alerts
const ALERTS = [
  { time: "14:32", company: "SCB", type: "critical", message: "Phát hiện bất nhất quán nghiêm trọng: NPL ratio mâu thuẫn (NNC = 0.05)" },
  { time: "14:28", company: "HPG", type: "warning", message: "Biên LNG không khớp giữa MD&A và BCKQKD (chênh lệch 2pp)" },
  { time: "14:15", company: "MWG", type: "warning", message: "Khẳng định BHX hòa vốn mâu thuẫn với thuyết minh phân khúc" },
  { time: "13:50", company: "VNM", type: "info", message: "Phân tích hoàn tất: 3/4 claims nhất quán, 1 bất nhất quán nhỏ" },
  { time: "13:45", company: "FPT", type: "success", message: "Kiểm tra hoàn tất: 3/3 claims nhất quán (NNC avg = 0.987)" }
];
