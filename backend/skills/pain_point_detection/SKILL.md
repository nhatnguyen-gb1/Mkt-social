name: pain_point_detection
version: 1.0.0
description: "Nhận diện nỗi đau và rào cản tài chính/thời gian của khách hàng."
purpose: "Xác định khó khăn khách hàng gặp phải."
inputs:
  - "message: Văn bản nói của khách"
outputs:
  - "pain_points": ["Rào cản 1", "Rào cản 2"]
workflow:
  - "Step 1: Phân tích nỗi đau khách hàng."
constraints: []
dependencies: []
