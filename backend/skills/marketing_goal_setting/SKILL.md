name: marketing_goal_setting
version: 1.0.0
description: "Thiết lập mục tiêu tiếp thị định lượng (SMART Goals)."
purpose: "Quy đổi mục tiêu doanh thu thành các chỉ số Traffic, Leads, CVR, ROAS và Orders."
inputs:
  - "target_revenue: Doanh thu mục tiêu"
  - "budget: Ngân sách tiếp thị"
outputs:
  - "target_orders: Số đơn hàng cần đạt"
  - "target_cpa: Chi phí CPA tối đa"
  - "target_roas: Tỷ lệ ROAS hòa vốn & mục tiêu"
workflow:
  - "Step 1: Tính toán AOV và số đơn hàng tối thiểu."
  - "Step 2: Xác định điểm hòa vốn ROAS."
constraints:
  - "Các chỉ số đo lường phải rõ ràng."
dependencies:
  - "business_analysis"
