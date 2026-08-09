# EXAMPLES FOR LEAD QUALIFICATION AGENT (10 SCENARIOS)

## Scenario 1: Khách có nhu cầu rõ ràng (Clear Intent & Budget)
- **CUSTOMER**: "Anh đang tìm căn 2 phòng ngủ khoảng 3 tỷ, chắc cuối tháng mới mua."
- **EXPECTED**: intent=BUY, product_interest="2BR", budget="~3B", timeline="END_OF_MONTH", missing_info=["location", "financing"], next_question="Dạ anh đang quan tâm căn hộ tại khu vực/quận nào ạ?", score=85.0, classification="HOT".

## Scenario 2: Khách chưa có nhu cầu (No Need / Exploring)
- **CUSTOMER**: "Anh chỉ xem cho biết thôi chứ chưa có ý định mua."
- **EXPECTED**: intent="EXPLORING", score=35.0, classification="COLD", next_question="Dạ em gửi brochure tham khảo qua Zalo khi nào cần anh xem thêm nhé ạ."

## Scenario 3: Khách đang tham khảo so sánh
- **CUSTOMER**: "Bên em có gì khác so với đối thủ A không?"
- **EXPECTED**: intent="COMPARING", missing_info=["budget", "timeline"], next_question="Phát hiện nhu cầu so sánh điểm khác biệt."

## Scenario 4: Khách đang bận (Busy / Callback)
- **CUSTOMER**: "Anh đang họp, gọi lại sau nhé."
- **EXPECTED**: intent="BUSY", next_action="SCHEDULE_CALLBACK", score=50.0, classification="WARM".

## Scenario 5: Khách từ chối thẳng (Rejection)
- **CUSTOMER**: "Tôi nhầm số rồi, đừng gọi nữa."
- **EXPECTED**: intent="REJECT", score=0.0, classification="INVALID", next_action="CLOSE_LEAD".

## Scenario 6: Khách cung cấp thông tin không đầy đủ
- **CUSTOMER**: "Tôi muốn tìm mua căn hộ giá rẻ."
- **EXPECTED**: missing_info=["budget", "location", "timeline"], next_question="Dạ ngân sách dự kiến của anh khoảng bao nhiêu ạ?"

## Scenario 7: Khách đưa thông tin mâu thuẫn
- **CUSTOMER**: "Tôi muốn mua biệt thự cao cấp nhưng ngân sách chỉ có 500 triệu."
- **EXPECTED**: flag="BUDGET_MISMATCH", score=30.0, classification="COLD".

## Scenario 8: Khách nhu cầu cao nhưng thiếu thông tin
- **CUSTOMER**: "Tôi cần chuyển nhượng mua ngay trong tuần này."
- **EXPECTED**: timeline="IMMEDIATE", missing_info=["budget", "product_interest"], next_question="Hỏi chi tiết loại hình sản phẩm."

## Scenario 9: Khách cần hỗ trợ vay ngân hàng
- **CUSTOMER**: "Tài chính anh có 1 tỷ, cần vay thêm 50% được không?"
- **EXPECTED**: financing="NEEDS_LOAN_50", budget="2B".

## Scenario 10: Khách mua đầu tư
- **CUSTOMER**: "Anh mua cho thuê lại, cần dòng tiền tốt."
- **EXPECTED**: purpose="INVESTMENT_RENTAL".
