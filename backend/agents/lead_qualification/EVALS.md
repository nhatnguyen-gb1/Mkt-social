# EVALUATION BENCHMARK FOR LEAD QUALIFICATION AGENT (20 TEST CASES)

## 1. Danh sách 20 Benchmark Test Cases
1. **Lead Intake**: Tiếp nhận hồ sơ Lead chính xác.
2. **Intent Detection**: Nhận diện chuẩn intent BUY/EXPLORING/BUSY/REJECT.
3. **Information Extraction**: Trích xuất đúng Budget, Product, Timeline.
4. **Missing Info Identification**: Xác định chính xác thuộc tính còn thiếu.
5. **Next Best Question Selection**: Chọn câu hỏi tiếp theo phù hợp bối cảnh.
6. **Context Tracking**: Duy trì đúng ngữ cảnh qua nhiều lượt nói.
7. **Objection Detection**: Nhận diện đúng loại phản đối (Giá/Thời gian/Bận).
8. **Need Detection**: Nhận diện nhu cầu ở thực vs đầu tư.
9. **Pain Point Detection**: Nhận diện đúng rào cản tài chính/thời gian.
10. **Lead Scoring Reasoning**: Giải thích căn cứ chấm điểm minh bạch.
11. **Classification Accuracy**: Phân loại HOT/WARM/COLD/INVALID chuẩn ngưỡng.
12. **Confidence Score Calculation**: Điểm tin cậy tỷ lệ thuận với bằng chứng.
13. **Hallucination Resistance**: Không bịa thông tin khi khách chưa nói.
14. **Busy Scenario Handling**: Đề xuất gọi lại nhẹ nhàng khi khách bận.
15. **Rejection Handling**: Dừng đàm thoại ngay khi khách từ chối dứt khoát.
16. **Sales Handoff Schema Integrity**: Tạo Handoff đầy đủ các trường yêu cầu.
17. **Rule Compliance**: Tuân thủ 100% quy tắc RULES.md.
18. **Multi-turn State Persistence**: Cập nhật Lead Qualification qua từng lượt nói.
19. **Consent Policy Gate**: Bắt buộc có thông báo danh tính AI.
20. **Configurable Threshold Compliance**: Phản ánh đúng điểm threshold cấu hình.

## 2. Tiêu chuẩn Pass
- `overall_score`: >= 80.0
