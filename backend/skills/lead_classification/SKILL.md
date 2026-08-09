name: lead_classification
version: 1.0.0
description: "Phân loại Lead (HOT/WARM/COLD/INVALID/UNKNOWN) theo ngưỡng điểm số cấu hình."
purpose: "Phân tầng Lead để xử lý ưu tiên."
inputs:
  - "score: Điểm số Lead"
outputs:
  - "classification: Phân loại Lead"
workflow:
  - "Step 1: Khớp điểm số với ngưỡng phân loại."
constraints: []
dependencies: []
