name: customer_information_extraction
version: 1.0.0
description: "Trích xuất thông tin cấu trúc BANT (Budget, Location, Timeline, Product, Financing)."
purpose: "Thu thập các thuộc tính định hình nhu cầu."
inputs:
  - "message: Câu nói khách hàng"
outputs:
  - "extracted_info: Thông tin trích xuất"
workflow:
  - "Step 1: Rút trích các thuộc tính nhu cầu."
constraints: []
dependencies: []
