name: product_validation
version: 1.0.0
description: "Xác thực độ phù hợp sản phẩm với thị trường (Product-Market Fit Validation)."
purpose: "Đánh giá xem sản phẩm có giải quyết vấn đề đủ lớn hay không trước khi đổ tiền chạy Ads lớn."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "pmf_score_status: Đánh giá PMF (HIGH_MATCH / MODERATE / POOR)"
  - "core_value_proposition: Giá trị cốt lõi giải quyết bài toán khách hàng"
  - "validation_tests: Các bài test nhỏ đề xuất để kiểm chứng"
workflow:
  - "Step 1: Đối chiếu tính năng sản phẩm với nỗi đau khách hàng."
  - "Step 2: Đánh giá độ phù hợp và đề xuất bài test ngầm."
constraints:
  - "Đánh giá trung thực, không vuốt ve sản phẩm yếu kém."
dependencies:
  - "customer_analysis"
