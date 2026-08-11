# Examples: qualification_financing

## Example 1: Explicit answer
**Customer**: Tôi định vay ngân hàng.
**Agent**: Dạ, em ghi nhận anh/chị có nhu cầu vay vốn ạ.
**Result**: field=financing_method, value=loan, provenance=STATED

## Example 2: Ambiguous answer
**Customer**: Tôi đang xem xét.
**Agent**: Dạ vâng, khi nào có quyết định anh/chị báo em nhé.
**Result**: field=financing_method, provenance=UNKNOWN

## Example 3: Refusal
**Customer**: Tôi chưa muốn quyết định.
**Agent**: Dạ không sao, vấn đề này có thể tính sau ạ.
**Result**: field=none, provenance=REFUSED
