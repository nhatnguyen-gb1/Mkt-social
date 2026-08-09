# PHASE 0 — AI LEAD QUALIFICATION SYSTEM: GITHUB OPEN SOURCE REVIEW

Báo cáo nghiên cứu, phân tích và đánh giá chuyên sâu các dự án nguồn mở trên GitHub liên quan đến **AI Outbound Voice Agent**, **Telephony Call Automation**, **Mobile Automation** và **Lead Qualification**.

---

## 📌 1. TỔNG QUAN CÁC REPOSITORY ĐƯỢC ĐÁNH GIÁ

| Repository | Thể loại | Giấy phép (License) | Độ phù hợp với AIMOS |
| :--- | :--- | :--- | :--- |
| `vocodedev/vocode-core` | Full-duplex Streaming Voice Engine | MIT License | **Rất cao** (Cơ sở tham khảo chuẩn cho Voice Pipeline Streaming Websocket) |
| `kirklandsig/AIReceptionist` | OpenAI Realtime Speech-to-Speech Receptionist | MIT License | **Rất cao** (Tham khảo mô hình Speech-to-Speech latency thấp) |
| `agenticmail/agenticmail` | Multimodal Messaging & Telephony MCP Infrastructure | MIT License | **Trung bình** (Tham khảo mô hình giao tiếp email/SMS/call đa kênh) |
| `MadeAgents/mobile-use` | Autonomous Android GUI Agent (Reflection & Exploration) | Apache 2.0 | **Thấp - Không phù hợp** (Nghiêng về GUI automation / Benchmark) |
| `ghost-in-the-droid/android-agent` | ADB / Device Farm MCP Agent cho Mobile Devices | MIT License | **Thấp - Không phù hợp** (Quá phức tạp, không ổn định bằng Telephony SIP/API) |
| `livekit/agents` (Bổ sung) | Real-time Multimodal Voice & Video Agent Framework | Apache 2.0 | **Rất cao** (Kiến trúc WebRTC/SIP Gateway cực kỳ mạnh mẽ) |
| `pipecat-ai/pipecat` (Bổ sung) | Framework cho Real-time Voice & Multimodal Conversational AI | MIT License | **Rất cao** (Tối ưu hóa Audio Processing Frame-based) |

---

## 🔍 2. CHI TIẾT ĐÁNH GIÁ TỪNG REPOSITORY

### 2.1. `vocodedev/vocode-core`
- **Purpose**: Framework mã nguồn mở cho phép xây dựng ứng dụng thoại AI thời gian thực (real-time voice agents) theo mô hình streaming full-duplex.
- **Architecture**: Mô hình Orchestrator decoupled kết nối Transport Layer (WebSockets / Twilio) $\rightarrow$ STT $\rightarrow$ LLM $\rightarrow$ TTS.
- **Voice Pipeline**: Streaming audio qua WebSocket, hỗ trợ endpointing tự động (detect ngắt lời / barge-in).
- **Telephony**: Tích hợp Twilio Telephony Server, hỗ trợ Inbound / Outbound calls qua PSTN.
- **STT**: Hỗ trợ Deepgram, AssemblyAI, Whisper, Google Speech.
- **LLM**: Kết nối OpenAI GPT-4, Anthropic Claude, Llama via LangChain / LiteLLM.
- **TTS**: Hỗ trợ ElevenLabs, PlayHT, Azure Speech, Cartesia.
- **Call Control**: Quản lý trạng thái cuộc gọi (Start, Mute, Transfer, Hangup).
- **Transcript**: Tự động ghi âm và tạo Transcript hội thoại theo thời gian thực (Speaker diarization).
- **Tool Calling**: Hỗ trợ Function Calling kích hoạt Action trong lúc đàm thoại.
- **CRM Integration**: Chưa tích hợp sẵn CRM (yêu cầu viết thêm custom tool / webhook).
- **Lead Qualification**: Không có sẵn module sàng lọc lead (chỉ cung cấp Voice Orchestration Engine).
- **Dependencies**: Python 3.10+, WebSockets, Pydantic, Twilio SDK.
- **Security & Production Readiness**: Production-ready cho voice streaming, hỗ trợ self-host 100%.
- **Điểm có thể học**: Kiến trúc chia tầng Transport $\rightarrow$ STT $\rightarrow$ LLM $\rightarrow$ TTS rành mạch, cơ chế xử lý barge-in (người dùng nói chen ngang khi AI đang nói).
- **Điểm không phù hợp**: Không có sẵn logic Lead Qualification, Lead Scoring hay CRM Integration.

---

### 2.2. `kirklandsig/AIReceptionist`
- **Purpose**: Hệ thống AI Receptionist tự host chạy trên OpenAI Realtime API (Speech-to-Speech) để trả lời điện thoại và đặt lịch.
- **Architecture**: Đơn giản hóa Voice Pipeline bằng cách dùng trực tiếp mô hình Speech-to-Speech của OpenAI, bỏ qua bước trung gian STT và TTS riêng lẻ.
- **Voice Pipeline**: Low-latency Speech-to-Speech audio streaming qua WebSockets.
- **Telephony**: Tích hợp Twilio / Telnyx SIP Trunking.
- **STT & TTS**: Tích hợp sẵn trong OpenAI Realtime Audio model.
- **LLM**: OpenAI gpt-4o-realtime-preview.
- **Call Control**: Đơn giản (Start call, End call, Transfer to human).
- **Transcript**: Tạo transcript tự động từ OpenAI Realtime session logs.
- **Tool Calling**: Khai báo function call để đặt lịch (Calendar integration).
- **CRM Integration**: Chưa có CRM (kết nối webhook đơn giản).
- **Lead Qualification**: Có thể cấu hình prompt để hỏi nhu cầu ban đầu.
- **Dependencies**: Node.js / Python, OpenAI WebSockets SDK, Twilio SDK.
- **Security**: Đạt chuẩn cơ bản, yêu cầu bảo mật OpenAI API key & Webhook Signature verification.
- **Production Readiness**: Sẵn sàng thử nghiệm (Beta), chi phí OpenAI Realtime API còn cao.
- **Điểm có thể học**: Trải nghiệm đàm thoại mượt mà gần như người thật nhờ độ trễ cực thấp (< 500ms) của Speech-to-Speech.
- **Điểm không phù hợp**: Phụ thuộc độc quyền vào OpenAI API (không thể self-host mô hình LLM/STT/TTS độc lập), chi phí chạy tính theo phút rất đắt đỏ.

---

### 2.3. `agenticmail/agenticmail`
- **Purpose**: Hạ tầng giao tiếp đa kênh (Email, SMS, Voice Call) dành cho AI Agents thông qua giao thức MCP (Model Context Protocol).
- **Architecture**: CLI & Microservice đóng vai trò Adapter cung cấp công cụ giao tiếp cho AI Agents.
- **Telephony & Voice**: Sử dụng API bên thứ 3 (Twilio / Retell AI) để khởi tạo cuộc gọi outbound.
- **CRM Integration & Lead Qualification**: Cung cấp công cụ lưu vết hội thoại, gửi SMS/Email xác nhận sau cuộc gọi.
- **Điểm có thể học**: Tư duy đóng gói công cụ giao tiếp dưới dạng MCP Tools để bất kỳ Agent nào trong hệ thống cũng có thể gọi.
- **Điểm không phù hợp**: Nặng về Email/SMS hơn là một hệ thống đàm thoại giọng nói chuyên sâu.

---

### 2.4. `MadeAgents/mobile-use` & `ghost-in-the-droid/android-agent` (Android Automation Repos)
- **Purpose**: Tự động hóa thao tác trên màn hình điện thoại Android bằng AI Vision & ADB / Accessibility Services.
- **Architecture**: Chụp ảnh màn hình điện thoại $\rightarrow$ Đưa qua Vision LLM $\rightarrow$ Xác định tọa độ tap/swipe $\rightarrow$ Gửi lệnh ADB.
- **Đánh giá đối với bài toán Outbound Call**:
  - **Điểm yếu chí mạng**: Tốc độ phản hồi cực kỳ chậm (2-5 giây cho mỗi thao tác tap), dễ vỡ luồng khi có thông báo rác hoặc cuộc gọi nhỡ, không thể can thiệp trực tiếp vào luồng Audio gốc của cuộc gọi trên điện thoại Android phổ thông mà không root máy.
  - **Độ tin cậy**: Độ tin cậy cho môi trường Production cực kỳ thấp (< 60%).
- **Kết luận**: **KHÔNG PHÙ HỢP** cho hệ thống Outbound Call chuyên nghiệp. SIP Telephony API (Twilio/Telnyx/Asterisk) vượt trội hoàn toàn về độ ổn định, tốc độ và khả năng mở rộng.

---

### 2.5. Dự án bổ sung: `livekit/agents` & `pipecat-ai/pipecat`
- **Purpose**: Các framework tiêu chuẩn công nghiệp năm 2026 cho Real-time Conversational Voice AI.
- **Điểm sáng giá**:
  - Tích hợp sẵn **SIP Gateway** cho phép nối trực tiếp vào tổng đài doanh nghiệp.
  - Hỗ trợ kiến trúc Frame-based pipeline linh hoạt (kết nối Whisper/Deepgram STT + Cartesia/ElevenLabs TTS + Custom LLM).
  - Quản lý trạng thái kết nối WebRTC/SIP chịu tải hàng nghìn cuộc gọi đồng thời.

---

## 🏆 3. BẢNG SO SÁNH LỰA CHỌN CÔNG NGHỆ (BENCHMARK SUMMARY)

| Tiêu chí | SIP / Telephony API (Twilio / Telnyx / Asterisk) | Android Phone Automation (ADB / MobileUse) |
| :--- | :--- | :--- |
| **Độ ổn định (Uptime)** | **99.99%** (Tiêu chuẩn Viễn thông) | Thấp (< 60%, dễ đứt kết nối ADB / kẹt UI) |
| **Độ trễ Audio (Latency)** | **Rất thấp (< 300ms)** qua WebSocket/RTP | Rất cao (2-5 giây do chụp màn hình & gửi lệnh tap) |
| **Chất lượng âm thanh** | Chuẩn Digital Audio (8kHz G.711 / 16kHz PCM) | Thu qua Micro thiết bị (dễ nhiễu môi trường) |
| **Khả năng Scale** | **Hàng ngàn cuộc gọi đồng thời** | Giới hạn 1 cuộc gọi / 1 thiết bị vật lý |
| **Can thiệp Audio (Barge-in)** | **Có** (Hỗ trợ ngắt lời tức thì) | Không thể ngắt lời tức thì |
| **Bảo mật & Compliance** | Tuân thủ chính sách viễn thông & Mã hóa | Rủi ro rò rỉ dữ liệu qua màn hình thiết bị |
