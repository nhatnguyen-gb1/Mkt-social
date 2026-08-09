name: product_market_fit_analysis
version: 1.0.0
description: "Phân tích và chấm điểm Product-Market Fit (PMF) 10 chiều."
purpose: "Đánh giá sự phù hợp giữa sản phẩm và thị trường."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "pmf_score: Điểm số PMF (0-100)"
  - "verdict: STRONG_MATCH / MODERATE / WEAK"
workflow:
  - "Step 1: Đánh giá PMF 10 chiều."
constraints: []
dependencies: []
