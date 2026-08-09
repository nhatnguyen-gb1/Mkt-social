name: competitor_analysis
version: 1.0.0
description: "Phân tích đối thủ cạnh tranh, mô hình kinh doanh, ưu/nhược điểm và khoảng trống thị trường."
purpose: "Xác định vị thế của các đối thủ trực tiếp & gián tiếp để tìm điểm khác biệt cốt lõi (USP)."
inputs:
  - "product_name: Tên sản phẩm"
  - "target_market: Thị trường tiêu dùng"
outputs:
  - "direct_competitors: Danh sách đối thủ trực tiếp"
  - "indirect_competitors: Danh sách đối thủ gián tiếp"
  - "competitor_advantages: Điểm mạnh của đối thủ"
  - "market_gaps: Khoảng trống thị trường chưa được đáp ứng tốt"
workflow:
  - "Step 1: Quét danh sách các thương hiệu cùng phân khúc."
  - "Step 2: Liệt kê đối thủ trực tiếp và gián tiếp."
  - "Step 3: Phân tích ưu nhược điểm của đối thủ."
  - "Step 4: Chỉ ra khoảng trống thị trường (Market Gap) khai thác."
constraints:
  - "Phải phân biệt rõ đối thủ trực tiếp và đối thủ gián tiếp."
  - "Không bôi nhọ đối thủ, tập trung vào phân tích tính năng/định vị."
dependencies:
  - "market_research"
