name: demand_analysis
version: 1.0.0
description: "Đánh giá nhu cầu mua hàng, khối lượng tìm kiếm và tần suất tiêu dùng của ngành hàng."
purpose: "Xác định liệu thị trường có sẵn nhu cầu chủ động hay cần kích cầu."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "search_volume_level: Mức độ volume tìm kiếm (HIGH / MEDIUM / LOW)"
  - "demand_nature: Bản chất nhu cầu (Chủ động / Thụ động / Bắt trend)"
  - "repeat_purchase_rate: Tỷ lệ mua lại ước tính"
workflow:
  - "Step 1: Phân tích tần suất tìm kiếm của khách hàng."
  - "Step 2: Phân loại bản chất lực cầu."
constraints:
  - "Phải phân biệt được nhu cầu bền vững vs nhu cầu ảo ngắn hạn."
dependencies: []
