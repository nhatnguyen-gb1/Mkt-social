# Examples: conversation_closing

## Example 1: Explicit answer
**Customer**: Ok, cảm ơn em.
**Agent**: Dạ, cảm ơn anh/chị. Chúc anh/chị một ngày tốt lành!
**Result**: field=closing_status, value=closed_gracefully, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Có gì nhắn qua Zalo nhé.
**Agent**: Dạ vâng, em sẽ nhắn qua Zalo cho anh/chị ạ. Chào anh/chị!
**Result**: field=closing_status, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi bận rồi, cúp máy đây.
**Agent**: Dạ vâng, chào anh/chị ạ.
**Result**: field=none, provenance=REFUSED
