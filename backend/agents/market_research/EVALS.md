# EVALUATION BENCHMARK FOR MARKET RESEARCH AGENT (20 TEST CASES)

## 1. Danh sách Test Cases Benchmark
1. **Research Quality**: Báo cáo có cấu trúc mạch lạc, đủ thông tin thị trường.
2. **Question Understanding**: Hiểu đúng mục tiêu nghiên cứu của người dùng.
3. **Research Planning**: Xây dựng kế hoạch nghiên cứu theo quy trình 12 bước.
4. **Evidence Handling**: Phân biệt chuẩn Fact, Evidence, Inference, Assumption, Unknown.
5. **Market Analysis**: Đánh giá quy mô thị trường TAM/SAM/SOM hợp lý.
6. **Customer Analysis**: Nhận diện đúng Pain points và Jobs To Be Done.
7. **Competitor Analysis**: Bản đồ định vị đối thủ chính xác.
8. **Trend Analysis**: Phân biệt đúng giữa Virality và Purchase Demand.
9. **Reasoning**: Khuyến nghị suy luận logic từ dữ liệu phân tích.
10. **Uncertainty Handling**: Báo rõ UNKNOWN khi thiếu thông tin.
11. **Hallucination Resistance**: Tuyệt đối không bịa số liệu ảo.
12. **Recommendation Quality**: Đưa ra hành động khả thi (GO / CAUTION / NO_GO).
13. **Output Structure**: Khớp 100% JSON ResearchReport schema contract.
14. **Rule Compliance**: Tuân thủ 100% RULES.md.
15. **Pricing Sweet Spot Analysis**: Nhận diện khoảng giá chốt đơn ngọt.
16. **Market Saturation Check**: Đánh giá mức bão hòa chính xác.
17. **Risk Assessment**: Chỉ ra rủi ro vi phạm chính sách & vận hành.
18. **Cross-Check Verification**: Kiểm tra chéo dữ liệu đa nguồn.
19. **Confidence Rating**: Điểm tin cậy (Confidence Score 0-100%) phù hợp với dữ liệu thu thập.
20. **Market Opportunity Scoring**: Điểm số Opportunity Score phản ánh đúng 9 chiều phân tích.

## 2. Tiêu chuẩn Chấm điểm (Scoring Metric)
- `overall_score`: 0 - 100
- Pass threshold: >= 70.0
