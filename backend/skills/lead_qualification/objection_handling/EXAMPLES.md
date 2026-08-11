# Examples: objection_handling

## Example 1: Explicit answer
**Customer**: Giá này cao quá.
**Agent**: Dạ em hiểu, nhưng chất lượng sản phẩm tương xứng anh/chị ạ.
**Result**: field=objection_type, value=price, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Tôi thấy cũng bình thường.
**Agent**: Dạ, anh/chị có điểm nào chưa hài lòng không ạ?
**Result**: field=objection_type, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Thôi bỏ đi.
**Agent**: Dạ vâng, em xin lỗi đã làm phiền.
**Result**: field=none, provenance=REFUSED
