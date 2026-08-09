name: budget_planning
version: 1.0.0
description: "Phân bổ ngân sách quảng cáo và quản lý chi phí tiếp thị."
purpose: "Chia ngân sách theo quy tắc 70-20-10 tối ưu rủi ro."
inputs:
  - "total_budget: Tổng ngân sách"
outputs:
  - "core_channel_budget: Ngân sách kênh chủ lực (70%)"
  - "testing_budget: Ngân sách thử nghiệm (20%)"
  - "reserve_budget: Ngân sách dự phòng (10%)"
workflow:
  - "Step 1: Áp dụng quy tắc 70-20-10 phân bổ ngân sách."
  - "Step 2: Ghi nhận hạn mức chi tiêu theo ngày."
constraints:
  - "Tổng các khoản phân bổ phải đúng bằng tổng ngân sách."
dependencies: []
