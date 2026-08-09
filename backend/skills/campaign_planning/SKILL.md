name: campaign_planning
version: 1.0.0
description: "Lập kế hoạch chiến dịch tiếp thị tổng thể theo các mốc thời gian."
purpose: "Xác định các pha triển khai chiến dịch (Test -> Scale -> Optimize)."
inputs:
  - "product_name: Tên sản phẩm"
  - "budget: Ngân sách"
outputs:
  - "campaign_phases: Các giai đoạn triển khai chiến dịch"
  - "duration_days: Tổng số ngày dự kiến"
workflow:
  - "Step 1: Phân chia chiến dịch thành Pha 1 Test ($50), Pha 2 Scale ($350), Pha 3 Remarketing ($100)."
  - "Step 2: Gắn timeline cụ thể từng pha."
constraints:
  - "Timeline phải thực tế."
dependencies: []
