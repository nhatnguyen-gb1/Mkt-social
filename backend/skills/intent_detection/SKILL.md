name: intent_detection
version: 1.0.0
description: "Phát hiện ý định đàm thoại của khách hàng (BUY/EXPLORING/BUSY/REJECT)."
purpose: "Xác định mục tiêu chính của câu nói."
inputs:
  - "message: Câu nói của khách hàng"
outputs:
  - "intent: Ý định đàm thoại"
workflow:
  - "Step 1: Phân tích ý định từ văn bản."
constraints: []
dependencies: []
