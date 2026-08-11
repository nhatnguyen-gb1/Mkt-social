from dataclasses import dataclass
from typing import Dict, List, Optional
from .state import ConversationState, CustomerState

@dataclass
class NextBestQuestion:
    field_target: str
    question_text: str
    style: str
    rationale: str
    priority: int

QUESTION_BANK: Dict[str, Dict[str, List[str]]] = {
    'budget': {
        'formal': [
            'Dạ, ngân sách dự kiến của anh/chị cho khoản đầu tư này là bao nhiêu ạ?',
            'Anh/chị có thể chia sẻ mức tài chính mình đang chuẩn bị được không ạ?',
            'Mức ngân sách mà anh/chị dự trù cho việc mua bất động sản này khoảng bao nhiêu ạ?'
        ],
        'friendly': [
            'Tầm tài chính anh/chị đang nhắm tới khoảng chừng bao nhiêu ạ?',
            'Anh/chị định đầu tư khoảng bao nhiêu tiền cho căn này vậy?',
            'Mình dự tính mua nhà tầm giá khoảng bao nhiêu anh/chị nhỉ?'
        ],
        'concise': [
            'Ngân sách dự kiến của mình là bao nhiêu ạ?',
            'Anh/chị mua tầm giá nào ạ?',
            'Khoảng giá anh/chị quan tâm là bao nhiêu?'
        ],
        'consultative': [
            'Để em lọc căn phù hợp nhất, anh/chị cho em biết tầm tài chính dự kiến nhé?',
            'Anh/chị chia sẻ khoảng ngân sách giúp em để em gửi vài phương án tối ưu ạ.',
            'Mức tài chính của mình ở khoảng nào để em tư vấn gói vay hoặc căn phù hợp nhất ạ?'
        ],
        'soft': [
            'Không biết tầm tài chính mình dự tính khoảng bao nhiêu, anh/chị chia sẻ để em hỗ trợ thêm nhé.',
            'Dạ, anh/chị có thể cho em biết khoảng giá mình mong muốn để em tìm căn vừa ý nhất không ạ?',
            'Em xin phép hỏi một chút về mức tài chính dự kiến để em tìm phương án nhẹ nhàng nhất cho mình ạ.'
        ]
    },
    'location': {
        'formal': [
            'Dạ, anh/chị đang quan tâm đến khu vực hoặc quận nào ạ?',
            'Anh/chị ưu tiên tìm vị trí ở khu vực nào thưa anh/chị?',
            'Vị trí bất động sản mà anh/chị mong muốn tọa lạc ở đâu ạ?'
        ],
        'friendly': [
            'Anh/chị thích tìm nhà ở khu nào nhất ạ?',
            'Mình đang ngắm nghía khu vực nào vậy anh/chị?',
            'Anh/chị ưu tiên mua ở quận nào nhất ạ?'
        ],
        'concise': [
            'Anh/chị tìm mua ở khu vực nào ạ?',
            'Mình chuộng quận nào nhất?',
            'Anh/chị định mua ở đâu ạ?'
        ],
        'consultative': [
            'Với nhu cầu của mình, anh/chị ưu tiên khu vực nào để tiện đi lại hay sinh hoạt nhất ạ?',
            'Anh/chị có nhắm đến khu vực nào cụ thể để em đánh giá tiềm năng tăng giá giúp mình không?',
            'Vị trí nào sẽ thuận tiện cho công việc và gia đình mình nhất ạ?'
        ],
        'soft': [
            'Dạ, không biết anh/chị thích ở khu vực nào để em tìm căn có môi trường tốt nhất ạ?',
            'Anh/chị có ưu tiên khu nào không ạ, chia sẻ để em hỗ trợ tìm kiếm kỹ hơn nhé.',
            'Em tìm ở khu vực nào thì sẽ hợp ý mình nhất ạ?'
        ]
    },
    'timeline': {
        'formal': [
            'Dạ, dự kiến khi nào anh/chị cần nhận nhà hoặc chốt giao dịch ạ?',
            'Anh/chị có kế hoạch mua vào thời điểm nào trong năm nay ạ?',
            'Thời gian dự kiến anh/chị muốn tiến hành mua là bao giờ ạ?'
        ],
        'friendly': [
            'Anh/chị định bao giờ thì mua ạ?',
            'Mình có cần nhận nhà gấp không anh/chị?',
            'Tầm tháng mấy thì anh/chị tính chốt căn này ạ?'
        ],
        'concise': [
            'Khi nào anh/chị dự định mua ạ?',
            'Anh/chị cần nhà thời điểm nào?',
            'Kế hoạch mua của mình là khi nào?'
        ],
        'consultative': [
            'Anh/chị dự tính mua trong khoảng thời gian nào để em chọn dự án có tiến độ phù hợp nhất?',
            'Để em tư vấn các chính sách thanh toán tốt nhất đợt này, anh/chị định mua vào khoảng tháng mấy ạ?',
            'Mình cần nhà trong năm nay hay năm sau để em lọc các dự án sắp bàn giao ạ?'
        ],
        'soft': [
            'Dạ, anh/chị cứ thong thả tìm hay mình đang cần mua gấp ạ?',
            'Không biết mình dự tính khi nào mua để em canh đợt mở bán giá tốt nhất cho mình ạ.',
            'Anh/chị có kế hoạch thời gian cụ thể chưa ạ, cứ chia sẻ em sẽ sắp xếp hỗ trợ nhé.'
        ]
    },
    'financing': {
        'formal': [
            'Dạ, anh/chị dự định thanh toán bằng vốn tự có hay cần hỗ trợ từ ngân hàng ạ?',
            'Anh/chị có nhu cầu sử dụng đòn bẩy tài chính không ạ?',
            'Về phương thức thanh toán, anh/chị tính dùng tiền mặt hay vay thêm ạ?'
        ],
        'friendly': [
            'Mình tính mua trả thẳng hay là vay ngân hàng thêm ạ?',
            'Anh/chị có định vay ngân hàng không, hay mình thanh toán tiền mặt luôn?',
            'Mình mua tiền mặt hay cần hỗ trợ vay góp vậy anh/chị?'
        ],
        'concise': [
            'Anh/chị vay ngân hàng hay trả tiền mặt?',
            'Mình có cần vay ngân hàng không ạ?',
            'Anh/chị định thanh toán thế nào?'
        ],
        'consultative': [
            'Hiện đang có nhiều gói lãi suất tốt, anh/chị có muốn em tư vấn phương án vay ngân hàng không ạ?',
            'Để cân đối dòng tiền tốt nhất, anh/chị định vay ngân hàng hay dùng vốn tự có ạ?',
            'Anh/chị thanh toán tiền mặt hay vay để em chọn chính sách chiết khấu tốt nhất cho mình?'
        ],
        'soft': [
            'Dạ, mình dùng vốn tự có hay có cần vay thêm một chút để dòng tiền thoải mái không ạ?',
            'Không biết anh/chị tính thanh toán sao ạ, nếu cần vay ngân hàng em sẽ hỗ trợ hồ sơ miễn phí nhé.',
            'Em hỏi nhỏ xíu là mình tính vay thêm hay dùng tiền có sẵn để em canh chính sách giảm giá ạ?'
        ]
    },
    'purpose': {
        'formal': [
            'Dạ, mục đích mua bất động sản này của anh/chị là để ở hay đầu tư ạ?',
            'Anh/chị đang tìm mua với mục tiêu an cư hay sinh lời thưa anh/chị?',
            'Nhu cầu chính của anh/chị đối với bất động sản này là gì ạ?'
        ],
        'friendly': [
            'Anh/chị mua căn này để ở hay để cho thuê, đầu tư ạ?',
            'Mình tìm nhà mua để gia đình ở hay để đầu tư vậy anh/chị?',
            'Anh/chị nhắm căn này mua ở hay để tích sản ạ?'
        ],
        'concise': [
            'Anh/chị mua để ở hay đầu tư?',
            'Mục đích mua của mình là gì ạ?',
            'Mình mua để làm gì ạ?'
        ],
        'consultative': [
            'Anh/chị mua để ở hay đầu tư, để em chọn căn có vị trí và thiết kế phù hợp nhất với nhu cầu nhé?',
            'Nếu mình mua đầu tư em sẽ chọn căn dễ thanh khoản, còn mua ở em sẽ ưu tiên không gian, ý anh/chị sao ạ?',
            'Mục đích mua của mình là gì để em phân tích dòng tiền hay môi trường sống cho chuẩn ạ?'
        ],
        'soft': [
            'Dạ, anh/chị mua căn này cho gia đình mình ở hay để đầu tư kiếm lời thêm ạ?',
            'Mình mua để dành, để ở hay đầu tư ạ, anh/chị chia sẻ để em tìm căn ưng ý nhất nhé.',
            'Không biết anh/chị định mua ở hay đầu tư để em dặn chủ nhà chừa lại nội thất phù hợp ạ.'
        ]
    },
    'product_interest': {
        'formal': [
            'Dạ, anh/chị đang tìm loại bất động sản nào ạ?',
            'Anh/chị quan tâm đến loại căn hộ nào hay nhà riêng lẻ ạ?',
            'Quy mô căn hộ mình đang hướng tới là bao nhiêu phòng ngủ ạ?'
        ],
        'friendly': [
            'Anh/chị đang tìm căn mấy phòng ngủ vậy ạ?',
            'Mình thích căn hộ kiểu nào nhất anh/chị?',
            'Anh/chị đang nhắm căn 2PN, 3PN hay loại khác ạ?'
        ],
        'concise': [
            'Anh/chị tìm loại căn nào ạ?',
            'Anh/chị cần mấy phòng ngủ?',
            'Mình tìm căn hộ hay nhà phố ạ?'
        ],
        'consultative': [
            'Để em gợi ý căn phù hợp, anh/chị cho em biết quy mô gia đình và nhu cầu phòng ngủ nhé?',
            'Anh/chị cần căn bao nhiêu phòng ngủ để phù hợp với gia đình mình nhất ạ?',
            'Căn hộ 2PN, 3PN hay penthouse sẽ phù hợp hơn với nhu cầu của anh/chị không ạ?'
        ],
        'soft': [
            'Dạ, anh/chị đang tìm căn mấy phòng ngủ ạ? Để em tìm đúng thứ mình cần nhé.',
            'Mình đang định tìm loại căn nào, anh/chị chia sẻ nhé để em lọc cho đúng.',
            'Không biết anh/chị định tìm căn kiểu nào, em gợi ý vài phương án cho mình xem nhé.'
        ]
    }
}

class QuestionStrategyEngine:
    def __init__(self):
        self.question_bank = QUESTION_BANK

    def get_field_priority(self, field: str) -> int:
        priorities = {
            'budget': 1,
            'location': 2,
            'timeline': 3,
            'financing': 4,
            'purpose': 5,
            'product_interest': 6,
        }
        return priorities.get(field, 99)

    def select_style(self, state: ConversationState) -> str:
        turn_count = len(state.turns)
        style_idx = turn_count % 5
        styles = ['friendly', 'formal', 'concise', 'consultative', 'soft']
        base_style = styles[style_idx]
        
        if state.customer_state in [CustomerState.RESISTANT, CustomerState.CONFUSED]:
            return 'soft'
        if state.customer_state == CustomerState.HIGH_INTENT:
            return 'concise'
        if state.customer_state == CustomerState.UNCERTAIN:
            return 'consultative'
            
        return 'friendly'

    def format_question(self, field: str, style: str, turn_count: int) -> str:
        options = self.question_bank.get(field, {}).get(style, [])
        if not options:
            return f"Anh/chị cho em hỏi về {field} ạ?"
        return options[turn_count % len(options)]

    def select_next_question(self, state: ConversationState) -> Optional[NextBestQuestion]:
        if state.customer_state in [CustomerState.BUSY, CustomerState.REFUSING]:
            return None

        # Determine fields that are NOT yet extracted AND NOT yet asked
        # (A field should only be asked ONCE; if not extracted after asking, move on)
        unknown_fields = [
            f for f in state.get_unknown_fields()
            if not state.has_field(f) and not state.was_asked(f)
        ]

        if not unknown_fields:
            return None

        # Sort by priority
        unknown_fields.sort(key=self.get_field_priority)
        target_field = unknown_fields[0]

        style = self.select_style(state)
        turn_count = len(state.turns)
        question_text = self.format_question(target_field, style, turn_count)
        priority = self.get_field_priority(target_field)

        # Mark as asked AFTER selecting (prevents re-asking same field)
        state.mark_asked(target_field)

        return NextBestQuestion(
            field_target=target_field,
            question_text=question_text,
            style=style,
            rationale=f"Customer state is {state.customer_state.name}, missing high priority field: {target_field}",
            priority=priority
        )

