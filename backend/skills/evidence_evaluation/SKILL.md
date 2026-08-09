name: evidence_evaluation
version: 1.0.0
description: "Thẩm định minh chứng dữ liệu phân tách Fact, Evidence, Inference, Assumption, Unknown."
purpose: "Đảm bảo tính trung thực dữ liệu và đánh giá điểm tin cậy (Confidence Score)."
inputs:
  - "market: Thị trường"
outputs:
  - "evidence": ["Bằng chứng 1", "Bằng chứng 2"]
  - "assumptions": ["Giả định 1"]
  - "unknowns": ["Chưa đủ dữ liệu 1"]
  - "confidence": 85
workflow:
  - "Step 1: Phân loại dữ liệu thu thập được thành Fact, Evidence, Inference, Assumption và Unknown."
constraints: []
dependencies: []
