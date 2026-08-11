# Examples: mind_change_detection

## Example 1: Explicit answer
**Customer**: Tôi muốn đổi sang khu vực khác.
**Agent**: Dạ, anh/chị muốn chuyển sang khu vực nào ạ?
**Result**: field=changed_field, value=location, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Có khi tôi mua chỗ khác.
**Agent**: Dạ, vậy anh/chị đang nhắm khu vực nào khác không ạ?
**Result**: field=changed_field, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Chuyện đó tính sau đi.
**Agent**: Dạ vâng, khi nào có quyết định anh/chị báo em nhé.
**Result**: field=none, provenance=REFUSED
