# Examples: qualification_purpose

## Example 1: Explicit answer
**Customer**: Tôi muốn mua để ở.
**Agent**: Dạ, em ghi nhận anh/chị cần mua để ở ạ.
**Result**: field=purchase_purpose, value=residential, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Có thể ở, có thể cho thuê.
**Agent**: Dạ, vậy anh/chị nghiêng về phương án nào hơn ạ?
**Result**: field=purchase_purpose, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi chưa biết nữa.
**Agent**: Dạ vâng, mình cứ tham khảo trước ạ.
**Result**: field=none, provenance=REFUSED
