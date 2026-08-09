name: synthetic_consumer_survey
version: 1.0.0
description: "Giả lập khảo sát tâm lý tiêu dùng (Synthetic Consumer Survey) đo lường mức độ sẵn sàng chi trả (Willingness to Pay)."
purpose: "Đánh giá mức độ chấp nhận giá của 100 persona khách hàng đại diện."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "willingness_to_pay: Mức giá khách hàng sẵn sàng trả"
  - "price_acceptance_rate: Tỷ lệ chấp nhận giá (%)"
workflow:
  - "Step 1: Khởi tạo bảng hỏi khảo sát giả lập."
  - "Step 2: Tổng hợp kết quả phản hồi của panel persona đại diện."
constraints:
  - "Báo rõ kết quả là giả lập mô phỏng."
dependencies: []
# Source Attribution: Inspired by BayramAnnakov/synthetic-market-research (MIT License)
