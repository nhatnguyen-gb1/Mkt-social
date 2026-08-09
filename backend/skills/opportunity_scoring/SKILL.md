name: opportunity_scoring
version: 1.0.0
description: "Chấm điểm cơ hội thương mại thị trường trên thang điểm 0 - 100 kèm lý giải chi tiết."
purpose: "Cung cấp chỉ số định lượng giúp Marketer đưa ra quyết định duyệt hoặc hủy dự án."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "opportunity_score: Điểm cơ hội (0 - 100)"
  - "score_breakdown: Chi tiết điểm theo từng tiêu chí"
  - "final_verdict: Kết luận khuyến nghị (GO / GO_WITH_CAUTION / NO_GO)"
workflow:
  - "Step 1: Chấm điểm Nhu cầu (Demand - max 30đ)."
  - "Step 2: Chấm điểm Mức độ cạnh tranh (Competition - max 20đ)."
  - "Step 3: Chấm điểm Biên lợi nhuận (Margin - max 25đ)."
  - "Step 4: Chấm điểm Xu hướng (Trend - max 25đ)."
  - "Step 5: Tổng hợp điểm và đưa ra khuyến nghị."
constraints:
  - "Tổng điểm phải bằng tổng các tiêu chí thành phần."
dependencies:
  - "market_research"
  - "competitor_analysis"
  - "pricing_analysis"
