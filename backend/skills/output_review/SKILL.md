name: output_review
version: 1.0.0
description: "Thẩm định và đánh giá chất lượng kết quả đầu ra của các Sub-agents."
purpose: "Chấm điểm kết quả theo 6 tiêu chí (0-100) và đưa ra quyết định ACCEPT / REJECT."
inputs:
  - "agent_name: Tên Agent thực thi"
  - "output_data: Kết quả làm việc"
outputs:
  - "review_score: Điểm thẩm định (0 - 100)"
  - "verdict: Quyết định (ACCEPT / REJECT)"
  - "feedback: Phản hồi cải thiện nếu bị REJECT"
workflow:
  - "Step 1: Đánh giá kết quả trên 6 tiêu chí (Accuracy, Completeness, Relevance, Evidence, Business Impact, Rule Compliance)."
  - "Step 2: So sánh với ngưỡng điểm Threshold (Mặc định 70đ)."
  - "Step 3: Trả về ACCEPT nếu >= 70, REJECT kèm feedback nếu < 70."
constraints:
  - "Threshold điểm phải có thể cấu hình được."
dependencies: []
