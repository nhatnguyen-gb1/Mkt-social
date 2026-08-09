name: objection_detection
version: 1.0.0
description: "Phát hiện câu từ chối hoặc phản đối của khách hàng (Giá/Thời gian/Uy tín)."
purpose: "Xác định các lý do phản đối."
inputs:
  - "message: Văn bản khách hàng"
outputs:
  - "objections": ["Phản đối 1", "Phản đối 2"]
workflow:
  - "Step 1: Phân tích phản đối từ câu nói."
constraints: []
dependencies: []
