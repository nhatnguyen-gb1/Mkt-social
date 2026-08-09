name: risk_analysis
version: 1.0.0
description: "Phân tích rủi ro thị trường, pháp lý, vi phạm chính sách quảng cáo và rủi ro vận hành."
purpose: "Cảnh báo sớm các nguy cơ làm đứt gãy chiến dịch quảng cáo."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "policy_risks: Rủi ro vi phạm chính sách quảng cáo"
  - "operational_risks: Rủi ro vận hành & chuỗi cung ứng"
  - "mitigation_strategies: Biện pháp giảm thiểu rủi ro đề xuất"
workflow:
  - "Step 1: Đánh giá sản phẩm so với chính sách cấm/hạn chế của Facebook & TikTok Ads."
  - "Step 2: Đánh giá rủi ro hàng giả, hàng nhái, vận chuyển vỡ hỏng."
  - "Step 3: Đưa ra giải pháp giảm thiểu (Mitigation)."
constraints:
  - "Cảnh báo rõ các từ khóa cấm chạy Ads."
dependencies: []
