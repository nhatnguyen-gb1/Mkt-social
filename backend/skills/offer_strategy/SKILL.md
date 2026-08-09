name: offer_strategy
version: 1.0.0
description: "Thiết kế gói Offer sản phẩm hấp dẫn không thể từ chối."
purpose: "Tăng tỷ lệ chốt đơn và giá trị trung bình đơn hàng (AOV)."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "core_offer: Chi tiết gói sản phẩm chính"
  - "bonuses: Quà tặng đi kèm"
  - "guarantee: Cam kết bảo hành / Đổi trả"
workflow:
  - "Step 1: Đóng gói sản phẩm chính kèm quà tặng gia tăng giá trị."
  - "Step 2: Đưa ra cam kết loại bỏ hoàn toàn rủi ro mua hàng."
constraints:
  - "Quà tặng phải liên quan trực tiếp đến nhu cầu sử dụng."
dependencies: []
