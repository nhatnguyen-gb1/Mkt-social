name: trend_analysis
version: 1.0.0
description: "Phân tích xu hướng thị trường, nội dung viral trên Social Media và từ khóa tìm kiếm nổi bật."
purpose: "Bắt trúng sóng xu hướng tiêu dùng để tạo nội dung tiếp thị ăn khách."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "trending_keywords: Các từ khóa tìm kiếm đang tăng vọt"
  - "viral_content_hooks: Các dạng nội dung đang thu hút nhiều tương tác nhất"
  - "seasonal_trends: Xu hướng theo mùa trong năm"
workflow:
  - "Step 1: Quét xu hướng tìm kiếm Google Trends & TikTok Creative Center."
  - "Step 2: Tổng hợp nhóm từ khóa & định dạng video hot."
constraints:
  - "Xu hướng phải còn thời hạn áp dụng thực tế."
dependencies: []
