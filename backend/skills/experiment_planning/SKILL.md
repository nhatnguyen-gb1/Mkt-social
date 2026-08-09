name: experiment_planning
version: 1.0.0
description: "Xây dựng kế hoạch thử nghiệm A/B Testing cho Ad Creatives, Offer và Landing Page."
purpose: "Tìm ra thông điệp chiến thắng (Winner) dựa trên dữ liệu thử nghiệm."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "ab_test_variables: Biến số thử nghiệm (Ad Copy / Image / Hook / Price)"
  - "success_criteria: Tiêu chí xác định phương án chiến thắng"
workflow:
  - "Step 1: Xác định biến số thử nghiệm (Single Variable Test)."
  - "Step 2: Đặt tiêu chí chiến thắng dựa trên CTR hoặc CPA."
constraints:
  - "Chỉ thay đổi 1 biến số cho mỗi đợt A/B test."
dependencies: []
