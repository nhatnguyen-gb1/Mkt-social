name: lead_scoring
version: 1.0.0
description: "Chấm điểm LeadScore (0-100) theo trọng số cấu hình minh bạch."
purpose: "Đánh giá mức độ tiềm năng của Lead."
inputs:
  - "qualification_data: Dữ liệu nhu cầu Lead"
outputs:
  - "score: Điểm số Lead (0-100)"
  - "reasoning: Giải thích căn cứ chấm điểm"
workflow:
  - "Step 1: Tính toán tổng điểm theo các tiêu chí."
constraints: []
dependencies: []
