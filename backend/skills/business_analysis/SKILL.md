name: business_analysis
version: 1.0.0
description: "Phân tích bối cảnh kinh doanh, năng lực doanh nghiệp và bài toán thị trường."
purpose: "Đánh giá khả năng thực thi và tính khả thi của mục tiêu kinh doanh."
inputs:
  - "objective: Mục tiêu kinh doanh"
  - "context: Bối cảnh doanh nghiệp"
outputs:
  - "business_type: Mô hình kinh doanh (E-commerce / B2B / SaaS)"
  - "feasibility_status: Đánh giá tính khả thi (FEASIBLE / HIGH_RISK)"
  - "core_constraints: Rào cản cốt lõi"
workflow:
  - "Step 1: Tiếp nhận objective và context."
  - "Step 2: Phân tích mô hình kinh doanh và rào cản tài chính/vận hành."
  - "Step 3: Trả về kết quả đánh giá sơ bộ bối cảnh."
constraints:
  - "Không suy đoán dữ liệu khi thiếu thông tin."
dependencies: []
