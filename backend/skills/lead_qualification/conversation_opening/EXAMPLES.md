# Examples: conversation_opening

## Example 1: Explicit answer
**Customer**: Tôi muốn quan tâm vấn đề này.
**Agent**: Dạ, em xin ghi nhận thông tin của anh/chị.
**Result**: field=customer_name_confirmed, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Để tôi xem lại đã.
**Agent**: Dạ vâng, khi nào anh/chị xem xong thì báo em nhé.
**Result**: field=customer_name_confirmed, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi không muốn cung cấp thông tin này.
**Agent**: Dạ không sao ạ, mình có thể trao đổi về vấn đề khác nhé.
**Result**: field=none, provenance=REFUSED
