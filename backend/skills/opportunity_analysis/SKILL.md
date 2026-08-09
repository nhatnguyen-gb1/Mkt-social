name: opportunity_analysis
version: 1.0.0
description: "Chấm điểm cơ hội thị trường dựa trên Khung Opportunity Scoring (0-100)."
purpose: "Đánh giá mức độ hấp dẫn của cơ hội kinh doanh."
inputs:
  - "market: Thị trường"
outputs:
  - "opportunity_score: Điểm số cơ hội"
  - "score_breakdown: Phân rã điểm 9 chiều"
  - "verdict: GO / CAUTION / NO_GO"
workflow:
  - "Step 1: Tính toán điểm cơ hội theo 9 chiều."
constraints: []
dependencies: []
