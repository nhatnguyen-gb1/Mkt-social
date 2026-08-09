name: retention_churn_prevention
version: 1.0.0
description: "Thiết kế chiến lược chăm sóc giữ chân khách hàng và chủ động phòng ngừa rủi ro rời bỏ (Churn Prevention)."
purpose: "Tăng giá trị trọn đời khách hàng (LTV) và kéo lại khách hàng ngưng mua."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "retention_sequences: Kịch bản chăm sóc tự động (Email / Zalo ZNS / SMS)"
  - "winback_offers: Ưu đãi đặc quyền cho khách hàng ngưng tương tác > 60 ngày"
workflow:
  - "Step 1: Xây dựng chuỗi kịch bản chăm sóc 3-7-30 ngày sau mua."
  - "Step 2: Đưa ra thông điệp tri ân và voucher kích cầu mua lại."
constraints:
  - "Tránh spam tin nhắn gây khó chịu cho khách hàng."
dependencies: []
# Source Attribution: Inspired by coreyhaines31/marketingskills (MIT License)
