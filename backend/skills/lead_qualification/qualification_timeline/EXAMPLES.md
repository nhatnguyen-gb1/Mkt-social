# Examples: qualification_timeline

## Example 1: Explicit answer
**Customer**: Tôi muốn mua trong tháng tới.
**Agent**: Dạ, em ghi nhận anh/chị cần mua trong tháng tới ạ.
**Result**: field=purchase_timeline, value=1 month, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Chưa vội lắm.
**Agent**: Dạ, mình cứ xem từ từ ạ.
**Result**: field=purchase_timeline, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi không biết chắc được.
**Agent**: Dạ không sao, khi nào cần anh/chị cứ báo em.
**Result**: field=none, provenance=REFUSED
