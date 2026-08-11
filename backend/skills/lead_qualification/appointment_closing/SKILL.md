name: appointment_closing
version: 1.0.0
description: Chốt lịch xem nhà/tư vấn
purpose: Thu thập thông tin hoặc xử lý tình huống hội thoại
skill_id: lead_qual_appointment_closing_v1
domain: lead_qualification
objective: Đạt được mục tiêu của skill
required_information:
- appointment_time
- appointment_type
optional_information: []
trigger_conditions:
- Điều kiện kích hoạt
question_strategy: progressive_disclosure
question_variations:
  formal:
  - Câu hỏi formal 1
  - Câu hỏi formal 2
  friendly:
  - Câu hỏi friendly 1
  - Câu hỏi friendly 2
  concise:
  - Câu hỏi concise 1
  - Câu hỏi concise 2
  consultative:
  - Câu hỏi consultative 1
  - Câu hỏi consultative 2
  soft:
  - Câu hỏi soft 1
  - Câu hỏi soft 2
expected_customer_patterns:
- type: EXPLICIT
  examples:
  - Ví dụ 1
  - Ví dụ 2
- type: REFUSAL
  examples:
  - Từ chối
  - Không muốn nói
extraction_rules:
- Chỉ extract khi rõ ràng
ambiguity_rules:
- Hỏi lại nếu không rõ
objection_rules:
- Tôn trọng khách hàng
next_actions:
  on_explicit: EXTRACT_AND_CONTINUE
  on_refusal: HANDLE_REFUSAL
  on_ambiguous: CLARIFY
stop_conditions:
- Đã hoàn thành mục tiêu
escalation_conditions:
- Cần hỗ trợ từ human agent
inputs:
- 'conversation_text: Text hội thoại'
- 'conversation_state: State hiện tại'
outputs:
- 'kết_quả: Giá trị extract được'
- 'provenance: STATED/INFERRED/UNKNOWN'
workflow:
- 'Step 1: Xác định context'
- 'Step 2: Thực hiện hành động'
- 'Step 3: Ghi nhận kết quả'
constraints:
- KHÔNG suy diễn vô căn cứ
- KHÔNG lặp câu hỏi
dependencies: []
