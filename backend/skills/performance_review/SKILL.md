name: performance_review
version: 1.0.0
description: "Phân tích và đánh giá hiệu suất tiếp thị của chiến dịch đang chạy."
purpose: "So sánh dữ liệu Ads thực tế với mục tiêu KPI ban đầu để đề xuất điều chỉnh."
inputs:
  - "campaign_metrics: Các chỉ số chiến dịch (ROAS, CPA, CTR)"
outputs:
  - "performance_status: Trạng thái chiến dịch (ON_TRACK / UNDERPERFORMING / CRITICAL)"
  - "optimization_actions: Đề xuất hành động điều chỉnh"
workflow:
  - "Step 1: So sánh ROAS & CPA thực tế với Target."
  - "Step 2: Đưa ra chỉ định tăng ngân sách hoặc tạm dừng."
constraints:
  - "Căn cứ trực tiếp vào chỉ số thực tế."
dependencies: []
