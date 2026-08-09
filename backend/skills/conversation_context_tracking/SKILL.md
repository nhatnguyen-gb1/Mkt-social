name: conversation_context_tracking
version: 1.0.0
description: "Duy trì nhật ký đàm thoại qua nhiều lượt nói (Multi-turn Context)."
purpose: "Theo dõi trạng thái thông tin đã biết và còn thiếu."
inputs:
  - "conversation_history: Lịch sử đàm thoại"
outputs:
  - "known_info": {}
  - "missing_info": []
workflow:
  - "Step 1: Tổng hợp trạng thái thông tin đàm thoại."
constraints: []
dependencies: []
