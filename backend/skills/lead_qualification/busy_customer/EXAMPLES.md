# Examples: busy_customer

## Example 1: Explicit answer
**Customer**: Giờ tôi bận, gọi lại lúc 5h chiều nhé.
**Agent**: Dạ vâng, em sẽ gọi lại anh/chị lúc 5h chiều nay ạ.
**Result**: field=callback_time, value=5pm, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Tôi đang bận.
**Agent**: Dạ, vậy em gọi lại cho anh/chị vào giờ nào được ạ?
**Result**: field=callback_time, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Đừng gọi lại cho tôi nữa.
**Agent**: Dạ vâng, em xin lỗi đã làm phiền.
**Result**: field=none, provenance=REFUSED
