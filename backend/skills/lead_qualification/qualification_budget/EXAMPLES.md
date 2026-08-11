# Examples: qualification_budget

## Example 1: Explicit answer
**Customer**: Tôi có khoảng 3 tỷ.
**Agent**: Dạ, em xin ghi nhận anh/chị có ngân sách khoảng 3 tỷ ạ.
**Result**: field=budget_amount, value=3000000000, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Để tôi tính toán lại xem sao.
**Agent**: Dạ vâng, anh/chị cân nhắc nhé.
**Result**: field=budget_amount, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi không muốn nói về tiền bạc lúc này.
**Agent**: Dạ không sao ạ, mình có thể trao đổi về khu vực trước nhé.
**Result**: field=none, provenance=REFUSED
