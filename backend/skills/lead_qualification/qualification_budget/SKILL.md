name: qualification_budget
version: 1.0.0
description: "Xác định ngân sách thực tế của khách hàng BĐS"
purpose: "Thu thập ngân sách chính xác để lọc sản phẩm phù hợp"
skill_id: lead_qual_budget_v1
domain: lead_qualification
objective: "Xác định khoảng ngân sách thực tế của khách hàng"
required_information: ["budget_amount", "budget_type"]
optional_information: ["financing_need", "cash_available"]
trigger_conditions:
  - "Khách hàng chưa cung cấp ngân sách"
  - "Ngân sách bị mâu thuẫn"
question_strategy: "progressive_disclosure"
question_variations:
  formal:
    - "Dạ anh/chị dự kiến tài chính khoảng bao nhiêu ạ?"
    - "Anh/chị có thể cho em biết ngân sách dự kiến không ạ?"
  friendly:
    - "Để em tư vấn đúng nhất, anh/chị đang tính tầm bao nhiêu ạ?"
    - "Anh/chị muốn giữ ngân sách trong khoảng nào ạ?"
  concise:
    - "Ngân sách của anh/chị?"
    - "Tầm bao nhiêu ạ?"
  consultative:
    - "Để em lọc đúng nhóm căn phù hợp, anh/chị đang tính khoảng ngân sách nào ạ?"
    - "Anh/chị muốn ưu tiên mức dưới 3 tỷ hay khoảng 3-4 tỷ ạ?"
  soft:
    - "Nếu tiện, anh/chị có thể chia sẻ ngân sách dự kiến không ạ?"
    - "Không nhất thiết phải chính xác, nhưng khoảng tầm nào thì em tìm sản phẩm phù hợp hơn ạ?"
expected_customer_patterns:
  - type: EXPLICIT
    examples: ["3 tỷ", "khoảng 3 tỷ", "tầm 3"]
  - type: RANGE
    examples: ["2-3 tỷ", "3 đến 4 tỷ"]
  - type: REFUSAL
    examples: ["không muốn nói", "đừng hỏi chuyện tiền"]
extraction_rules:
  - "Chỉ extract khi khách hàng nói số tiền trực tiếp"
  - "Range phải ghi nhận cả lower_bound và upper_bound"
  - "KHÔNG suy diễn ngân sách từ loại sản phẩm"
ambiguity_rules:
  - "Nếu AMBIGUOUS → hỏi làm rõ một lần"
  - "Nếu REFUSAL → không hỏi lại ngân sách, chuyển sang field khác"
objection_rules:
  - "Không ép khách nói ngân sách nếu từ chối"
  - "Ghi nhận REFUSAL vào state"
next_actions:
  on_explicit: "EXTRACT_AND_CONTINUE"
  on_range: "EXTRACT_RANGE_AND_CONTINUE"
  on_refusal: "SKIP_BUDGET_ASK_LOCATION"
  on_ambiguous: "CLARIFY_ONCE"
  on_unknown: "ASK_BUDGET_QUESTION"
stop_conditions:
  - "Budget đã được xác nhận"
  - "Khách từ chối 2 lần"
escalation_conditions:
  - "Mâu thuẫn ngân sách phát hiện"
inputs:
  - "conversation_text: Text hội thoại"
  - "conversation_state: State hiện tại"
outputs:
  - "budget_extracted: Ngân sách đã extract"
  - "provenance: STATED/INFERRED/UNKNOWN"
workflow:
  - "Step 1: Kiểm tra state xem đã có ngân sách chưa"
  - "Step 2: Chọn câu hỏi phù hợp theo style"
  - "Step 3: Extract giá trị từ câu trả lời"
  - "Step 4: Ghi provenance"
constraints:
  - "KHÔNG suy diễn provenance STATED từ dữ liệu INFERRED"
  - "KHÔNG lặp câu hỏi giống nhau"
dependencies: []
