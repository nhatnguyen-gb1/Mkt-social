name: market_report
version: 1.0.0
description: "Đóng gói và định dạng Báo cáo Nghiên cứu Thị trường hoàn chỉnh từ các kết quả phân tích kỹ thuật."
purpose: "Tạo báo cáo thẩm mỹ, cô đọng, giàu giá trị hành động cho CMO và Marketer."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường"
  - "research_data: Kết quả tổng hợp từ các Skill trước"
outputs:
  - "executive_summary: Tóm tắt cho cấp quản lý"
  - "key_takeaways: 3 điểm cốt lõi cần nhớ"
  - "recommended_next_steps: Các bước triển khai tiếp theo"
workflow:
  - "Step 1: Thu thập kết quả từ các skill thành phần."
  - "Step 2: Cấu trúc thành bản báo cáo phân cấp rõ ràng."
  - "Step 3: Đưa ra danh sách công việc đề xuất (Action Items)."
constraints:
  - "Trình bày mạch lạc, trực quan, chuyên nghiệp."
dependencies:
  - "market_research"
  - "competitor_analysis"
  - "customer_analysis"
  - "opportunity_scoring"
