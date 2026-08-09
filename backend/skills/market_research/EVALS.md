# Đánh giá & Benchmark cho Market Research Skill

## Test Case 1: Standard Product Research
- **Input**: `{"product_name": "Bánh Trung Thu", "target_market": "Vietnam"}`
- **Expected Behavior**: Trả về bức tranh thị trường bánh trung thu tại Việt Nam theo mùa vụ.
- **Expected Output Characteristics**:
  - Có ước tính quy mô hoặc xu hướng mua sắm mùa lễ hội.
  - Có các động lực chính (quà tặng doanh nghiệp, xu hướng giảm đường).
- **Rules to Verify**:
  - `rule_compliance`: Không bịa đặt số liệu thống kê vô lý.
  - `completeness`: Phải có đủ 4 trường thông tin trả về.
  - `format_compliance`: Đúng định dạng JSON hoặc Markdown cấu trúc.
