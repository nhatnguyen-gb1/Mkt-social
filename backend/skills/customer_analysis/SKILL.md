name: customer_analysis
version: 1.0.0
description: "Phân tích chân dung khách hàng mục tiêu, tâm lý hành vi (Psychographics) và điểm đau (Pain Points)."
purpose: "Xây dựng cấu trúc Persona chi tiết làm đầu vào cho góc độ sáng tạo quảng cáo."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường tiêu dùng"
outputs:
  - "target_demographics: Độ tuổi, giới tính, thu nhập, vị trí địa lý"
  - "pain_points: Danh sách các vấn đề khó chịu nhất khách hàng đang gặp"
  - "desires_and_goals: Mong muốn cốt lõi khi dùng sản phẩm"
  - "buying_barriers: Rào cản tâm lý khiến họ ngần ngại chốt đơn"
workflow:
  - "Step 1: Xác định nhóm khách hàng mua nhiều nhất (Core Persona)."
  - "Step 2: Phân tích nỗi đau (Pain Points) và động lực mua hàng."
  - "Step 3: Phân tích rào cản chi tiêu và nghi ngờ phổ biến."
constraints:
  - "Nỗi đau phải cụ thể, tránh diễn đạt chung chung."
dependencies:
  - "market_research"
