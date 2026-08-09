name: agent_selection
version: 1.0.0
description: "Khảo sát và lựa chọn AI Agent chuyên trách phù hợp nhất cho từng nhiệm vụ."
purpose: "Đảm bảo đúng việc - đúng Agent. Báo lỗi Agent unavailable nếu chưa hỗ trợ."
inputs:
  - "task_description: Mô tả nhiệm vụ"
outputs:
  - "selected_agent: Tên Agent được chỉ định"
  - "agent_status: Trạng thái của Agent (READY / UNAVAILABLE)"
workflow:
  - "Step 1: Đối chiếu mô tả nhiệm vụ với danh sách Agent trong AgentRegistry."
  - "Step 2: Chỉ định Agent chuyên trách hoặc ghi nhận Agent unavailable."
constraints:
  - "Không giả vờ Agent đã chạy nếu Agent chưa tồn tại."
dependencies: []
