name: market_overview
version: 1.0.0
description: "Phân tích bức tranh tổng quan và quy mô thị trường (TAM, SAM, SOM)."
purpose: "Đưa ra đánh giá tổng quát về quy mô, tốc độ tăng trưởng và rào cản ngành."
inputs:
  - "market: Thị trường mục tiêu"
  - "product: Sản phẩm/Ngành hàng"
outputs:
  - "tam_estimate: Tổng thị trường tiềm năng"
  - "growth_rate: Tốc độ tăng trưởng hàng năm"
  - "market_stage: Giai đoạn thị trường (Tăng trưởng / Bão hòa)"
workflow:
  - "Step 1: Thu thập thông tin quy mô thị trường."
  - "Step 2: Đánh giá giai đoạn phát triển ngành."
constraints:
  - "Không bịa số quy mô thị trường."
dependencies: []
