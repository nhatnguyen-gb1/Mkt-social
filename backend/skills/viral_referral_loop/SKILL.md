name: viral_referral_loop
version: 1.0.0
description: "Thiết kế cơ chế giới thiệu lan truyền (Viral Referral Loops) kích thích người dùng tự nhân bản khách hàng mới."
purpose: "Giảm chỉ số CAC bằng cách khuyến khích khách hàng hiện tại rủ bạn bè mua chung."
inputs:
  - "product_name: Tên sản phẩm"
outputs:
  - "referral_incentive: Phần thưởng cho người giới thiệu và người được giới thiệu"
  - "viral_mechanics: Cơ chế chia sẻ (Mã giảm giá đôi / Quà tặng giới thiệu)"
workflow:
  - "Step 1: Thiết kế gói thưởng 2 chiều (Win-Win Referral Incentive)."
  - "Step 2: Đơn giản hóa nút chia sẻ 1-click qua Zalo / Facebook Messenger."
constraints:
  - "Phần thưởng phải thực sự thu hút cả 2 bên."
dependencies: []
# Source Attribution: Inspired by whyashthakker/agent-skills-marketing (MIT License)
