name: final_recommendation
version: 1.0.0
description: "Tổng hợp kết quả chỉ đạo, phân tách dữ liệu và đưa ra khuyến nghị tiếp thị cuối cùng."
purpose: "Đóng gói báo cáo phân tách Fact, Inference, Assumption, Recommendation và Unknown cho CMO."
inputs:
  - "objective: Mục tiêu ban đầu"
outputs:
  - "facts: Dữ liệu thực tế xác thực"
  - "inferences: Suy luận chiến lược"
  - "assumptions: Giả định cần kiểm chứng"
  - "unknowns: Dữ liệu thiếu cần bổ sung"
  - "recommendations: Danh sách khuyến nghị hành động"
workflow:
  - "Step 1: Phân tách minh bạch dữ liệu Fact, Inference, Assumption, Unknown."
  - "Step 2: Đưa ra danh sách 3 khuyến nghị hành động ưu tiên cao nhất."
constraints:
  - "Không biến Assumption thành Fact."
dependencies: []
