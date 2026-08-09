name: market_research
version: 1.0.0
description: "Phân tích tổng quan dung lượng, tốc độ phát triển và cấu trúc thị trường cho sản phẩm mục tiêu."
purpose: "Cung cấp bức tranh toàn cảnh về quy mô thị trường, xu hướng tăng trưởng và bối cảnh ngành hàng."
inputs:
  - "product_name: Tên sản phẩm hoặc dịch vụ"
  - "target_market: Thị trường địa lý (Mặc định: Vietnam)"
outputs:
  - "market_size_estimate: Ước tính quy mô thị trường"
  - "growth_rate: Tốc độ tăng trưởng hàng năm (CAGR)"
  - "market_drivers: Các động lực thúc đẩy thị trường"
  - "summary: Tóm tắt tổng quan thị trường"
workflow:
  - "Step 1: Xác định định nghĩa ngành hàng và sản phẩm mục tiêu."
  - "Step 2: Thu thập thông tin quy mô thị trường và CAGR hiện tại."
  - "Step 3: Phân tích các động lực vi mô và vĩ mô."
  - "Step 4: Tổng hợp tóm tắt nhận định thị trường."
constraints:
  - "Không tự bịa đặt số liệu thống kê nếu thiếu bằng chứng."
  - "Phải ghi rõ nguồn dữ liệu hoặc ghi nhận UNKNOWN nếu chưa xác thực."
dependencies: []
