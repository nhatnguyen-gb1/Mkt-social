# PHASE 0 — AI LEAD QUALIFICATION SYSTEM: ARCHITECTURE PROPOSAL

Bản thiết kế Kiến trúc Tổng thể (Master Architecture Proposal) cho module **AI Lead Qualification System** trong AIMOS.

---

## 🏗️ 1. KHUNG KIẾN TRÚC TỔNG THỂ (SYSTEM ARCHITECTURE FLOW)

Sơ đồ luồng dữ liệu end-to-end từ lúc tiếp nhận Lead đến khi Handoff cho đội ngũ Sales:

```text
               +-------------------------------------------------+
               |              Lead Entry Point                   |
               |     (API / Webform / File Import / Ads Lead)     |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |          Eligibility & Policy Gate              |
               |  (Consent Check, DNC List, Call Time Window)    |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |              Outbound Call Queue                |
               |        (Prioritization & Rate Limiting)         |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |            Call Engine (WebSocket Server)       |
               +-------------------------------------------------+
                  /                     |                     \
                 /                      v                      \
                v               +---------------+               v
         +--------------+       | Conversation  |       +--------------+
         |     STT      | ----> |    Engine     | ----> |     TTS      |
         | (Speech-to-  |       | (Context &    |       | (Text-to-    |
         |    Text)     |       | State Machine)|       |   Speech)    |
         +--------------+       +---------------+       +--------------+
                                        |
                                        v
                                +---------------+
                                |  LLM Engine   |
                                |(Intent & Tool)|
                                +---------------+
                                        |
                                        v
               +-------------------------------------------------+
               |            Qualification Engine                 |
               |      (Extract BANT / Intent / Requirements)     |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |         Configurable Lead Scoring Engine        |
               |   (Calculate LeadScore & Segment Hot/Warm/Cold) |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |           Transcript & Summary Generator        |
               |      (Generate Actionable Call Brief & Record)  |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |                  CRM Adapter                    |
               |   (Sync Lead Score, Notes & Qualification Data) |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |                 Sales Handoff                   |
               |  (Route to Sales Rep / Auto-Book Appointment)   |
               +-------------------------------------------------+
                                        |
                                        v
               +-------------------------------------------------+
               |            Telegram Notification Bot            |
               |   (Instant Alert for Hot Lead with Call Summary)|
               +-------------------------------------------------+
```

---

## 🔌 2. NGUYÊN TẮC THIẾT KẾ ABSTRACTION LAYERS (PROVIDER INTERFACES)

Để đảm bảo hệ thống không bị khóa chặt (lock-in) vào bất kỳ Vendor nào, tất cả các thành phần cốt lõi đều được trừu tượng hóa qua các Interface chuẩn:

### 2.1. `TelephonyProvider` Interface
Quản lý kết nối viễn thông (Khởi tạo cuộc gọi, nhận diện tín hiệu bắt máy, gửi/nhận luồng audio WebSocket, kết thúc cuộc gọi).
- **Các triển khai hỗ trợ**: `TwilioTelephonyProvider`, `TelnyxTelephonyProvider`, `SIPTrunkProvider`, `AndroidADBProvider` (chỉ dùng thử nghiệm dev/test).

### 2.2. `SpeechToTextProvider` Interface
Biến đổi luồng âm thanh đầu vào (Audio Stream) thành văn bản thời gian thực (Real-time Streaming Transcripts).
- **Các triển khai hỗ trợ**: `DeepgramSTTProvider`, `AssemblyAISTTProvider`, `WhisperLiveProvider` (Self-hosted), `GoogleSTTProvider`.

### 2.3. `LanguageModelProvider` Interface
Xử lý logic hội thoại, hiểu câu trả lời của khách hàng và đưa ra phản hồi tiếp theo.
- **Các triển khai hỗ trợ**: `OpenAILLMProvider`, `AnthropicLLMProvider`, `OllamaSelfHostedProvider`, `MockLLMProvider`.

### 2.4. `TextToSpeechProvider` Interface
Tổng hợp văn bản phản hồi thành luồng âm thanh tự nhiên (Audio Stream) để phát lại cho khách hàng.
- **Các triển khai hỗ trợ**: `ElevenLabsTTSProvider`, `CartesiaTTSProvider`, `AzureSpeechTTSProvider`, `PiperTTSProvider` (Self-hosted).

### 2.5. `CRMProvider` Interface
Cập nhật và đồng bộ dữ liệu Lead, điểm số Qualification và tóm tắt cuộc gọi vào hệ thống CRM của doanh nghiệp.
- **Các triển khai hỗ trợ**: `HubSpotCRMProvider`, `SalesforceCRMProvider`, `ZOHOCRMProvider`, `InternalAIMOSCRMProvider`.

### 2.6. `LeadScoringEngine` Interface
Khung tính toán điểm số Lead (0-100) theo cấu hình linh hoạt từng ngành hàng.

---

## 🎙️ 3. VOICE PIPELINE & STREAMING MECHANICS

1. **Full-Duplex Audio Streaming**: Đàm thoại 2 chiều qua giao thức WebSocket (16kHz PCM audio).
2. **Barge-in / Interruption Handling**: Nhận diện ngay lập tức khi khách hàng cất tiếng nói trong lúc AI đang nói $\rightarrow$ Lập tức tạm dừng luồng TTS và hủy các frame âm thanh đang chờ phát.
3. **VAD & Endpointing (Voice Activity Detection)**: Xác định chính xác khi nào khách hàng kết thúc câu nói (silence threshold 400-600ms) để gửi dữ liệu về cho LLM.
