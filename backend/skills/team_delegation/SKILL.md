name: team_delegation
version: 1.0.0
description: "Phân rã mục tiêu chiến dịch thành danh sách công việc giao cho Sub-agents."
purpose: "Tạo luồng Task Plan minh bạch giữa Marketing Lead và các Sub-agents."
inputs:
  - "objective: Mục tiêu tổng thể"
outputs:
  - "task_plan: Kế hoạch phân rã từng bước"
workflow:
  - "Step 1: Phân rã mục tiêu thành các nhiệm vụ nghiên cứu, sáng tạo, quảng cáo và đo lường."
  - "Step 2: Ghi nhận luồng phụ thuộc giữa các công việc."
constraints:
  - "Mỗi bước trong task plan phải có mục tiêu rõ ràng."
dependencies: []
