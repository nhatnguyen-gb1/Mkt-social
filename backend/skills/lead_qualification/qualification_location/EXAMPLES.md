# Examples: qualification_location

## Example 1: Explicit answer
**Customer**: Tôi muốn mua nhà ở Quận 7.
**Agent**: Dạ, em xin ghi nhận anh/chị tìm nhà ở Quận 7 ạ.
**Result**: field=preferred_location, value=Quận 7, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Chỗ nào cũng được.
**Agent**: Dạ, để thu hẹp tìm kiếm, anh/chị có ưu tiên gần chỗ làm không ạ?
**Result**: field=preferred_location, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi chưa biết nữa.
**Agent**: Dạ không sao, mình từ từ cân nhắc ạ.
**Result**: field=none, provenance=REFUSED
