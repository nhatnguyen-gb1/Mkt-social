name: customer_problem_analysis
version: 1.0.0
description: "Phân tích bài toán nỗi đau và nhu cầu mua hàng của khách hàng."
purpose: "Chỉ ra 3 nỗi đau lớn nhất mà sản phẩm có thể giải quyết dứt điểm."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "primary_pain_points: Các điểm đau chính"
  - "buying_triggers: Ngòi nổ tâm lý chốt đơn"
workflow:
  - "Step 1: Liệt kê bài toán khó chịu của người dùng."
  - "Step 2: Gắn ngòi nổ tâm lý chốt đơn nhanh."
constraints:
  - "Nỗi đau phải cụ thể và thực tế."
dependencies: []
