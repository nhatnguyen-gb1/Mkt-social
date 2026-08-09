name: pricing_analysis
version: 1.0.0
description: "Phân tích khoảng giá thị trường, giá chấp nhận mua và biên lợi nhuận kỳ vọng."
purpose: "Đề xuất khoảng giá tối ưu hóa tỷ lệ chuyển đổi quảng cáo."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
outputs:
  - "price_range: Dải giá phổ biến trên thị trường"
  - "sweet_spot_price: Mức giá chuyển đổi tốt nhất cho Ads"
  - "margin_assessment: Đánh giá biên lợi nhuận"
workflow:
  - "Step 1: Quét dải giá bán lẻ thị trường."
  - "Step 2: Xác định điểm ngọt (Sweet spot price) dễ chốt đơn."
constraints:
  - "Giá tiền trình bày rõ đơn vị VND hoặc USD."
dependencies: []
