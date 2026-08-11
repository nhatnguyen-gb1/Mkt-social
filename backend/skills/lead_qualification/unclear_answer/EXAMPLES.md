# Examples: unclear_answer

## Example 1: Explicit answer
**Customer**: Ý tôi là tôi muốn xem nhà vào cuối tuần.
**Agent**: Dạ, vậy em chốt lịch cho anh/chị vào cuối tuần nhé.
**Result**: field=clarification_status, value=clarified, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Cái nào cũng được.
**Agent**: Dạ, để em chọn phương án tối ưu nhất cho mình ạ.
**Result**: field=clarification_status, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Thôi bỏ qua đi.
**Agent**: Dạ vâng, mình chuyển sang vấn đề khác ạ.
**Result**: field=none, provenance=REFUSED
