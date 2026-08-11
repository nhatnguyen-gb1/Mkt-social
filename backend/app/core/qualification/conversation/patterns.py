from dataclasses import dataclass
from typing import Dict, List, Optional
from .state import ResponseType, CustomerState

@dataclass
class PatternEntry:
    input_text: str
    normalized_value: str
    response_type: str
    confidence: float
    evidence_hint: str
    expected_action: str

@dataclass
class MatchResult:
    field: str
    matched_pattern: str
    normalized_value: str
    response_type: str   # string value e.g. "EXPLICIT", "RANGE"
    confidence: float
    evidence: str
    expected_action: str


def _generate_budget_patterns() -> List[PatternEntry]:
    patterns = []
    
    # Explicit (20+)
    explicit_bases = ['3 tỷ', '3 tỉ', '3ty', '3ti', 'ba tỷ', 'ba tỉ', 'ba ty', '3b', '3B']
    for b in explicit_bases:
        patterns.append(PatternEntry(f'Tầm {b}', '3000000000', ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))
        patterns.append(PatternEntry(f'Khoảng {b}', '3000000000', ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))
        patterns.append(PatternEntry(b, '3000000000', ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))
        patterns.append(PatternEntry(f'Có khoảng {b}', '3000000000', ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))
    
    # Additional explicit patterns for common amounts
    extra_amounts = [
        ('có khoảng 3', '3000000000'), ('có khoảng 3 tỷ', '3000000000'),
        ('có khoảng 3,5', '3500000000'), ('có khoảng 4 tỷ', '4000000000'),
        ('5 tỷ', '5000000000'), ('tầm 5 tỷ', '5000000000'), ('khoảng 5 tỷ', '5000000000'),
        ('5 tỉ', '5000000000'), ('5b', '5000000000'),
        ('1.5 tỷ', '1500000000'), ('tầm 1.5 tỷ', '1500000000'), ('1,5 tỷ', '1500000000'),
        ('2.5 tỷ', '2500000000'), ('anh có khoảng 2.5 tỷ', '2500000000'),
        ('1 tỷ rưỡi', '1500000000'), ('2 tỷ rưỡi', '2500000000'),
        ('4 tỷ', '4000000000'), ('4 tỉ', '4000000000'), ('tầm 4 tỷ', '4000000000'),
        ('6 tỷ', '6000000000'), ('7 tỷ', '7000000000'), ('8 tỷ', '8000000000'),
        ('1 tỷ', '1000000000'), ('2 tỷ', '2000000000'), ('tầm 2 tỷ', '2000000000'),
    ]
    for text, val in extra_amounts:
        patterns.append(PatternEntry(text, val, ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))

    # Slang (15+)
    slangs = [('30 lẻ', '3000000000'), ('35 lẻ', '3500000000'), ('2 xịn', '2000000000'), ('3 xịn', '3000000000'), 
              ('1 ky rưỡi', '1500000000'), ('2 ky', '2000000000'), ('3 ky', '3000000000'), ('hai ký', '2000000000'), ('ba ký', '3000000000'),
              ('2 đồng', '2000000000'), ('3 đồng', '3000000000'), ('4 đồng', '4000000000'), ('3 tỏi', '3000000000'),
              ('tầm 30', '3000000000'), ('tầm 30 lẻ', '3000000000'), ('tầm 25', '2500000000'), ('tầm 20', '2000000000'),
              ('20 lẻ', '2000000000'), ('25 lẻ', '2500000000'), ('40 lẻ', '4000000000'),
    ]
    for s, v in slangs:
        patterns.append(PatternEntry(s, v, ResponseType.EXPLICIT.value, 0.8, 'stated slang', 'CONTINUE'))
        patterns.append(PatternEntry(f'Tầm {s}', v, ResponseType.EXPLICIT.value, 0.8, 'stated slang', 'CONTINUE'))

    # Range (20+)
    ranges = ['2-3 tỷ', '3 đến 4 tỷ', '2,5 đến 3 tỷ', 'từ 2 đến 3', 'tầm 2-3', 'khoảng 3-4 tỷ', 'từ 3 tới 4',
              'tầm 2 tới 3 tỉ', '2-3', '3-4 tỉ', '3-4 tỷ', 'tầm 3-4 tỷ', 'tầm 3-4', '2.5 đến 3', '1-2 tỷ', '4-5 tỷ']
    for r in ranges:
        patterns.append(PatternEntry(r, r, ResponseType.RANGE.value, 0.85, 'stated range', 'CONTINUE'))
        patterns.append(PatternEntry(f'khoảng {r}', r, ResponseType.RANGE.value, 0.85, 'stated range', 'CONTINUE'))

    # Upper bound (15+)
    uppers = ['tối đa 3 tỷ', 'không quá 3', 'dưới 3 tỷ', 'dưới 3.5 tỷ', 'tầm dưới 3', 'cao nhất 3 tỷ',
              'cùng lắm 3 tỷ', 'không hơn 3 tỷ', 'tầm dưới 3.5 tỷ', 'không quá 3.5 tỷ', 'không quá 4 tỷ',
              'dưới 5 tỷ', 'không quá 5 tỷ', 'tối đa 4 tỷ', 'tối đa 5 tỷ']
    for u in uppers:
        patterns.append(PatternEntry(u, '3000000000', ResponseType.UPPER_BOUND.value, 0.85, 'stated max', 'CONTINUE'))

    # Lower bound (15+)
    lowers = ['ít nhất 2 tỷ', 'từ 3 tỷ trở lên', 'trên 3 tỷ', 'tối thiểu 2 tỷ', 'trên hai tỉ',
              'ít nhất 3 tỷ', 'từ 2 tỷ', 'từ 4 tỷ', 'trên 4 tỷ', 'tối thiểu 3 tỷ']
    for l in lowers:
        patterns.append(PatternEntry(l, '3000000000', ResponseType.LOWER_BOUND.value, 0.85, 'stated min', 'CONTINUE'))

    # Implicit (10+)
    implicits = ['mua trả góp', 'vay ngân hàng', 'anh có tiền mặt khoảng 1 tỷ', 'đang kẹt tiền', 'phải vay thêm']
    for i in implicits:
        patterns.append(PatternEntry(i, 'UNKNOWN', ResponseType.IMPLICIT.value, 0.7, 'implied financing', 'CLARIFY'))

    # Unknown (10+)
    unknowns = ['chưa tính', 'chưa biết', 'em tư vấn đi', 'tính sau', 'chưa rõ', 'để xem lại', 'không rành']
    for u in unknowns:
        patterns.append(PatternEntry(u, 'UNKNOWN', ResponseType.UNKNOWN.value, 0.8, 'stated unknown', 'CLARIFY'))

    # Refusal (10+)
    refusals = ['đừng hỏi chuyện tiền', 'không muốn nói', 'sao hỏi nhiều vậy', 'riêng tư', 'không tiện nói', 'chưa mua nên chưa nói']
    for r in refusals:
        patterns.append(PatternEntry(r, 'UNKNOWN', ResponseType.REFUSAL.value, 0.9, 'refused', 'ESCALATE'))

    # Ambiguous (10+)
    ambiguous = ['tầm đó', 'khoảng đó thôi', 'cỡ đó', 'vừa vừa', 'bình thường', 'không nhiều', 'tương đối']
    for a in ambiguous:
        patterns.append(PatternEntry(a, 'UNKNOWN', ResponseType.AMBIGUOUS.value, 0.7, 'vague', 'CLARIFY'))

    # Fill to 100+: generate additional amounts
    for i in range(20):
        patterns.append(PatternEntry(f'khoảng {2+i} tỷ', f'{2000000000+i*1000000000}', ResponseType.EXPLICIT.value, 0.9, 'stated exact', 'CONTINUE'))

    return patterns

def _generate_location_patterns() -> List[PatternEntry]:
    patterns = []
    locs = [
        ('Quận 7', 'Q7'), ('Q7', 'Q7'), ('quận bảy', 'Q7'), ('Quận Bảy', 'Q7'),
        ('Quận 2', 'Q2'), ('Q2', 'Q2'), ('quận hai', 'Q2'), ('Thủ Đức', 'Thủ Đức'),
        ('Bình Chánh', 'Bình Chánh'), ('Bình Tân', 'Bình Tân'), ('Gò Vấp', 'Gò Vấp'), ('Tân Bình', 'Tân Bình'),
        ('Gần trung tâm', 'Trung Tâm'), ('khu vực trung tâm', 'Trung Tâm'), ('không quá xa trung tâm', 'Trung Tâm'),
        ('Gần trường học', 'Tiện ích'), ('gần bệnh viện', 'Tiện ích'), ('gần chỗ làm', 'Tiện ích')
    ]
    for text, val in locs:
        patterns.append(PatternEntry(text, val, ResponseType.EXPLICIT.value, 0.9, 'stated loc', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh kiếm khu {text}', val, ResponseType.EXPLICIT.value, 0.9, 'stated loc', 'CONTINUE'))
        patterns.append(PatternEntry(f'tầm {text}', val, ResponseType.EXPLICIT.value, 0.8, 'stated loc', 'CONTINUE'))

    unknowns = ['chưa biết', 'chỗ nào cũng được', 'tùy', 'em đề xuất đi', 'đâu cũng được', 'chưa chốt', 'đang xem']
    for u in unknowns:
        patterns.append(PatternEntry(u, 'UNKNOWN', ResponseType.UNKNOWN.value, 0.8, 'stated unknown', 'CLARIFY'))

    for i in range(1, 13):
        patterns.append(PatternEntry(f'Quận {i}', f'Q{i}', ResponseType.EXPLICIT.value, 0.9, 'stated loc', 'CONTINUE'))
        patterns.append(PatternEntry(f'Q{i}', f'Q{i}', ResponseType.EXPLICIT.value, 0.9, 'stated loc', 'CONTINUE'))
    
    return patterns

def _generate_timeline_patterns() -> List[PatternEntry]:
    patterns = []
    urgents = ['cuối tháng', 'tháng này', 'tuần này', 'mua ngay', 'cần gấp', 'sắp tới', 'ngay bây giờ', 'trong tháng', 'mua liền']
    for u in urgents:
        patterns.append(PatternEntry(u, 'URGENT', ResponseType.EXPLICIT.value, 0.9, 'urgent', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh cần {u}', 'URGENT', ResponseType.EXPLICIT.value, 0.9, 'urgent', 'CONTINUE'))

    mids = ['3 tháng', '6 tháng', 'quý sau', 'cuối năm', 'đầu năm sau', 'vài tháng nữa', 'qua tết']
    for m in mids:
        patterns.append(PatternEntry(m, 'MID_TERM', ResponseType.EXPLICIT.value, 0.9, 'mid term', 'CONTINUE'))
        patterns.append(PatternEntry(f'chắc {m}', 'MID_TERM', ResponseType.EXPLICIT.value, 0.9, 'mid term', 'CONTINUE'))

    non_urgents = ['chưa vội', 'sang năm', 'tính từ từ', 'chưa cần gấp', 'xem xét từ từ', 'lâu dài', 'năm sau', 'còn lâu']
    for n in non_urgents:
        patterns.append(PatternEntry(n, 'NON_URGENT', ResponseType.EXPLICIT.value, 0.9, 'non urgent', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {n}', 'NON_URGENT', ResponseType.EXPLICIT.value, 0.9, 'non urgent', 'CONTINUE'))

    unknowns = ['chưa biết', 'tùy', 'chưa quyết định', 'tới đâu hay tới đó', 'tùy tình hình']
    for u in unknowns:
        patterns.append(PatternEntry(u, 'UNKNOWN', ResponseType.UNKNOWN.value, 0.8, 'unknown', 'CLARIFY'))
        
    for i in range(1, 13):
        patterns.append(PatternEntry(f'tháng {i}', f'Tháng {i}', ResponseType.EXPLICIT.value, 0.9, 'exact month', 'CONTINUE'))
        patterns.append(PatternEntry(f'trong tháng {i}', f'Tháng {i}', ResponseType.EXPLICIT.value, 0.9, 'exact month', 'CONTINUE'))
        
    return patterns

def _generate_financing_patterns() -> List[PatternEntry]:
    patterns = []
    mortgages = ['muốn vay', 'cần vay ngân hàng', 'vay 50%', 'vay 70%', 'có hỗ trợ vay không', 'trả góp', 'vay bank']
    for m in mortgages:
        patterns.append(PatternEntry(m, 'MORTGAGE', ResponseType.EXPLICIT.value, 0.9, 'needs mortgage', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {m}', 'MORTGAGE', ResponseType.EXPLICIT.value, 0.9, 'needs mortgage', 'CONTINUE'))
        patterns.append(PatternEntry(f'muốn {m}', 'MORTGAGE', ResponseType.EXPLICIT.value, 0.9, 'needs mortgage', 'CONTINUE'))
        
    cash = ['tiền mặt', 'không vay', 'trả thẳng', 'đủ tiền', 'có sẵn', 'thanh toán một lần']
    for c in cash:
        patterns.append(PatternEntry(c, 'CASH', ResponseType.EXPLICIT.value, 0.9, 'has cash', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh có {c}', 'CASH', ResponseType.EXPLICIT.value, 0.9, 'has cash', 'CONTINUE'))
        patterns.append(PatternEntry(f'muốn {c}', 'CASH', ResponseType.EXPLICIT.value, 0.9, 'has cash', 'CONTINUE'))

    unclear = ['chưa biết', 'tùy', 'xem thêm', 'tùy lãi suất', 'để coi đã', 'tính sau']
    for u in unclear:
        patterns.append(PatternEntry(u, 'UNKNOWN', ResponseType.UNKNOWN.value, 0.8, 'unclear financing', 'CLARIFY'))
        
    for i in range(30, 90, 10):
        patterns.append(PatternEntry(f'vay {i}%', f'MORTGAGE_{i}', ResponseType.EXPLICIT.value, 0.9, 'exact pct', 'CONTINUE'))
    
    return patterns

def _generate_purpose_patterns() -> List[PatternEntry]:
    patterns = []
    live = ['để ở', 'ở thực', 'cho gia đình ở', 'vợ chồng ở', 'mua ở', 'mua cho con', 'ra riêng', 'tìm chỗ ở']
    for l in live:
        patterns.append(PatternEntry(l, 'LIVE', ResponseType.EXPLICIT.value, 0.9, 'living', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {l}', 'LIVE', ResponseType.EXPLICIT.value, 0.9, 'living', 'CONTINUE'))
        patterns.append(PatternEntry(f'muốn {l}', 'LIVE', ResponseType.EXPLICIT.value, 0.9, 'living', 'CONTINUE'))

    invest = ['đầu tư', 'cho thuê', 'sinh lời', 'dòng tiền', 'tích sản', 'mua đi bán lại', 'đầu cơ', 'lướt sóng']
    for i in invest:
        patterns.append(PatternEntry(i, 'INVEST', ResponseType.EXPLICIT.value, 0.9, 'investment', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {i}', 'INVEST', ResponseType.EXPLICIT.value, 0.9, 'investment', 'CONTINUE'))
        patterns.append(PatternEntry(f'muốn {i}', 'INVEST', ResponseType.EXPLICIT.value, 0.9, 'investment', 'CONTINUE'))

    unknown = ['chưa biết', 'tùy', 'vừa ở vừa đầu tư', 'tính sau', 'chưa rõ']
    for u in unknown:
        patterns.append(PatternEntry(u, 'UNKNOWN', ResponseType.UNKNOWN.value, 0.8, 'unclear purpose', 'CLARIFY'))
    
    return patterns

def _generate_intent_patterns() -> List[PatternEntry]:
    patterns = []
    buy = ['muốn mua', 'đang tìm mua', 'tìm hiểu mua', 'cần mua', 'đang xem nhà', 'tìm nhà']
    for b in buy:
        patterns.append(PatternEntry(b, 'BUY', ResponseType.EXPLICIT.value, 0.9, 'wants to buy', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {b}', 'BUY', ResponseType.EXPLICIT.value, 0.9, 'wants to buy', 'CONTINUE'))

    invest = ['muốn đầu tư', 'mua để đầu tư', 'đang tìm dự án', 'xem đầu tư']
    for i in invest:
        patterns.append(PatternEntry(i, 'INVEST', ResponseType.EXPLICIT.value, 0.9, 'wants to invest', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {i}', 'INVEST', ResponseType.EXPLICIT.value, 0.9, 'wants to invest', 'CONTINUE'))

    rent = ['muốn thuê', 'tìm thuê', 'cần thuê', 'thuê nhà']
    for r in rent:
        patterns.append(PatternEntry(r, 'RENT', ResponseType.EXPLICIT.value, 0.9, 'wants to rent', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {r}', 'RENT', ResponseType.EXPLICIT.value, 0.9, 'wants to rent', 'CONTINUE'))

    browse = ['xem thôi', 'tham khảo', 'chỉ xem', 'đang dạo', 'lướt xem', 'chưa tính mua']
    for br in browse:
        patterns.append(PatternEntry(br, 'BROWSING', ResponseType.EXPLICIT.value, 0.9, 'browsing', 'CONTINUE'))
        patterns.append(PatternEntry(f'anh {br}', 'BROWSING', ResponseType.EXPLICIT.value, 0.9, 'browsing', 'CONTINUE'))

    reject = ['nhầm số', 'không phải tôi', 'sai số', 'gọi nhầm rồi', 'lộn số']
    for rj in reject:
        patterns.append(PatternEntry(rj, 'REJECT', ResponseType.REFUSAL.value, 0.9, 'wrong number', 'CLOSE'))
        patterns.append(PatternEntry(f'bạn {rj}', 'REJECT', ResponseType.REFUSAL.value, 0.9, 'wrong number', 'CLOSE'))

    return patterns

def _generate_objections_patterns() -> List[PatternEntry]:
    patterns = []
    price = ['giá cao quá', 'đắt quá', 'không đủ tiền', 'hơi chát', 'quá khả năng', 'vượt ngân sách']
    for p in price:
        patterns.append(PatternEntry(p, 'PRICE_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'price issue', 'CLARIFY'))
        patterns.append(PatternEntry(f'anh thấy {p}', 'PRICE_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'price issue', 'CLARIFY'))

    time = ['chưa quyết định', 'để anh suy nghĩ', 'chưa vội', 'từ từ', 'xem xét đã']
    for t in time:
        patterns.append(PatternEntry(t, 'TIME_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'timing issue', 'CLARIFY'))
        patterns.append(PatternEntry(f'anh {t}', 'TIME_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'timing issue', 'CLARIFY'))

    social = ['phải hỏi vợ', 'phải hỏi chồng', 'bàn với gia đình', 'hỏi ý kiến người nhà', 'vợ quyết định']
    for s in social:
        patterns.append(PatternEntry(s, 'SOCIAL_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'needs consensus', 'CLARIFY'))
        patterns.append(PatternEntry(f'anh {s}', 'SOCIAL_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'needs consensus', 'CLARIFY'))

    info = ['gửi thông tin trước', 'email cho anh', 'zalo đi', 'nhắn tin qua zalo', 'gửi qua đây',
            'gửi thông tin qua', 'qua email', 'gửi qua email', 'nhắn zalo', 'gửi brochure']
    for i in info:
        patterns.append(PatternEntry(i, 'INFO_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'wants async info', 'CLARIFY'))
        patterns.append(PatternEntry(f'em {i}', 'INFO_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'wants async info', 'CLARIFY'))

    comp = ['đang xem nhiều bên', 'đang tham khảo thêm', 'có sale khác tư vấn rồi', 'bạn anh cũng giới thiệu']
    for c in comp:
        patterns.append(PatternEntry(c, 'COMPETITION_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'shopping around', 'CLARIFY'))
        patterns.append(PatternEntry(f'anh {c}', 'COMPETITION_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'shopping around', 'CLARIFY'))

    distrust = ['không tin tưởng', 'em nói vậy thôi', 'dự án lừa đảo', 'mấy vụ này sợ lắm']
    for d in distrust:
        patterns.append(PatternEntry(d, 'DISTRUST_OBJECTION', ResponseType.OBJECTION.value, 0.9, 'lacks trust', 'CLARIFY'))

    return patterns

def _generate_refusal_patterns() -> List[PatternEntry]:
    patterns = []
    busy = ['đang bận', 'đang họp', 'gọi lại sau', 'bận rồi', 'đang chạy xe', 'lúc khác gọi']
    for b in busy:
        patterns.append(PatternEntry(b, 'BUSY', ResponseType.REFUSAL.value, 0.9, 'busy', 'CALLBACK'))
        patterns.append(PatternEntry(f'anh {b}', 'BUSY', ResponseType.REFUSAL.value, 0.9, 'busy', 'CALLBACK'))
        patterns.append(PatternEntry(f'chị {b}', 'BUSY', ResponseType.REFUSAL.value, 0.9, 'busy', 'CALLBACK'))

    refuse = ['đừng gọi nữa', 'không cần', 'thôi khỏi', 'không có nhu cầu', 'đừng làm phiền', 'xóa số đi']
    for r in refuse:
        patterns.append(PatternEntry(r, 'REFUSAL', ResponseType.REFUSAL.value, 0.9, 'hard refusal', 'CLOSE'))
        patterns.append(PatternEntry(f'anh {r}', 'REFUSAL', ResponseType.REFUSAL.value, 0.9, 'hard refusal', 'CLOSE'))

    ambiguous = ['à', 'ừ', 'hmm', 'để xem', 'tính xem', 'ồ', 'thế à', 'vậy sao', 'ờ', 'thế à', 'xem sao']
    for a in ambiguous:
        patterns.append(PatternEntry(a, 'AMBIGUOUS', ResponseType.AMBIGUOUS.value, 0.7, 'vague', 'CONTINUE'))
        patterns.append(PatternEntry(f'ờ {a}', 'AMBIGUOUS', ResponseType.AMBIGUOUS.value, 0.7, 'vague', 'CONTINUE'))
        
    for i in range(10):
        patterns.append(PatternEntry(f'gọi lại lúc {i+1} giờ', 'BUSY', ResponseType.REFUSAL.value, 0.9, 'busy', 'CALLBACK'))
        
    return patterns

PATTERN_LIBRARY: Dict[str, List[PatternEntry]] = {
    'budget': _generate_budget_patterns(),
    'location': _generate_location_patterns(),
    'timeline': _generate_timeline_patterns(),
    'financing': _generate_financing_patterns(),
    'purpose': _generate_purpose_patterns(),
    'intent': _generate_intent_patterns(),
    'objections': _generate_objections_patterns(),
    'refusal_busy_ambiguous': _generate_refusal_patterns()
}

class ResponsePatternMatcher:
    def __init__(self):
        self.library = PATTERN_LIBRARY

    def match(self, text: str, field: str) -> Optional[MatchResult]:
        text_lower = text.lower()
        best_match = None
        highest_conf = -1.0
        
        patterns = self.library.get(field, [])
        for p in patterns:
            if p.input_text.lower() in text_lower:
                if p.confidence > highest_conf:
                    highest_conf = p.confidence
                    best_match = MatchResult(
                        field=field,
                        matched_pattern=p.input_text,
                        normalized_value=p.normalized_value,
                        response_type=p.response_type,  # already a string
                        confidence=p.confidence,
                        evidence=text,
                        expected_action=p.expected_action
                    )
        return best_match

    def detect_customer_state(self, text: str) -> CustomerState:
        import re
        text_lower = text.lower()

        def _matches(pattern_text: str, target: str) -> bool:
            p_lower = pattern_text.lower()
            # For very short patterns (<=3 chars), require word boundary to avoid
            # false positives like "ồ" matching inside "rồi"
            if len(p_lower) <= 3:
                return bool(re.search(r'(?<!\w)' + re.escape(p_lower) + r'(?!\w)', target))
            return p_lower in target

        # Check refusal/busy first (highest priority)
        for p in self.library['refusal_busy_ambiguous']:
            if _matches(p.input_text, text_lower):
                if p.normalized_value == 'BUSY':
                    return CustomerState.BUSY
                elif p.normalized_value == 'REFUSAL':
                    return CustomerState.REFUSING
                elif p.normalized_value == 'AMBIGUOUS':
                    return CustomerState.UNCERTAIN

        # Check intent (buy/invest = HIGH_INTENT, browsing = CURIOUS, reject = REFUSING)
        for p in self.library['intent']:
            if _matches(p.input_text, text_lower):
                if p.normalized_value in ['BUY', 'INVEST']:
                    return CustomerState.HIGH_INTENT
                elif p.normalized_value == 'BROWSING':
                    return CustomerState.CURIOUS
                elif p.normalized_value == 'REJECT':
                    return CustomerState.REFUSING

        # Check objections (RESISTANT or UNCERTAIN for timing/hesitation) — after intent
        for p in self.library['objections']:
            if p.input_text.lower() in text_lower:
                val = p.normalized_value
                if val in ('NOT_READY', 'NEED_TIME', 'UNCERTAIN', 'NOT_URGENT',
                           'TIME_OBJECTION', 'SOCIAL_OBJECTION'):
                    return CustomerState.UNCERTAIN
                return CustomerState.RESISTANT

        return CustomerState.UNKNOWN

    def detect_objection(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for p in self.library['objections']:
            if p.input_text.lower() in text_lower:
                return p.normalized_value
        return None

    def get_all_patterns(self) -> Dict[str, List[PatternEntry]]:
        return self.library

    def count_patterns(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.library.items()}
