name: mom_test_validation
version: 1.0.0
description: "Thẩm định giả định sản phẩm bằng khung Mom Test chống hứa suông."
purpose: "Đánh giá bằng chứng hành vi quá khứ của người dùng."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "validation_score: Điểm tin cậy Mom Test (0-100)"
  - "decision: VALIDATE / ITERATE / REJECT"
workflow:
  - "Step 1: Kiểm thử giả định qua khung Mom Test."
constraints: []
dependencies: []
# Source Attribution: Inspired by mom-test-interview-framework (MIT License)
