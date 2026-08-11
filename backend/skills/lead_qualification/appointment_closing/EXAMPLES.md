# Examples: appointment_closing

## Example 1: Explicit answer
**Customer**: Chiều thứ 7 tôi rảnh.
**Agent**: Dạ, vậy em đặt lịch cho anh/chị chiều thứ 7 nhé.
**Result**: field=appointment_time, value=Saturday afternoon, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Có thể cuối tuần này.
**Agent**: Dạ, cuối tuần này anh/chị rảnh thứ 7 hay Chủ Nhật ạ?
**Result**: field=appointment_time, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tuần này tôi bận hết rồi.
**Agent**: Dạ vâng, qua tuần em xin phép liên hệ lại nhé.
**Result**: field=none, provenance=REFUSED
