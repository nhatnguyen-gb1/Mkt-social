# HƯỚNG DẪN CẤU HÌNH & THỬ NGHIỆM TELEGRAM BOT CHO AIMOS

Tài liệu hướng dẫn chi tiết cách khởi tạo Bot Telegram, lấy Bot Token, lấy Telegram User ID, cấu hình môi trường `.env` và chạy thử nghiệm hai chiều với hệ thống **AIMOS**.

---

## 🛠️ 1. HƯỚNG DẪN TẠO TELEGRAM BOT & LẤY TOKEN

### Bước 1: Tạo Bot qua @BotFather
1. Mở ứng dụng Telegram trên điện thoại hoặc máy tính.
2. Tìm kiếm từ khóa `@BotFather` và chọn tài khoản có tích xanh chính chủ.
3. Nhấn **Start** hoặc gõ lệnh `/newbot`.
4. Nhập tên hiển thị cho Bot (Ví dụ: `AIMOS Marketing Bot`).
5. Nhập tên người dùng (username) cho Bot (Phải kết thúc bằng chữ `bot`, ví dụ: `aimos_marketing_demo_bot`).
6. Sau khi tạo thành công, `@BotFather` sẽ gửi cho bạn chuỗi **HTTP API Token** (Ví dụ: `7123456789:AAFxxx_your_real_bot_token_here`).

> ⚠️ **CẢNH BÁO BẢO MẬT**: Tuyệt đối **KHÔNG** chia sẻ Bot Token hoặc push token lên Git repository công khai.

---

### Bước 2: Lấy Telegram User ID của bạn
1. Mở Telegram, tìm kiếm bot `@userinfobot` hoặc `@myidbot`.
2. Nhấn **Start** hoặc gửi tin nhắn bất kỳ.
3. Bot sẽ trả về dãy số **Id** của bạn (Ví dụ: `123456789`). Dãy số này chính là `TELEGRAM_ALLOWED_USER_IDS`.

---

## ⚙️ 2. CẤU HÌNH FILE `.ENV` TRÊN AIMOS

Mở tệp `.env` trong thư mục `C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend\.env` (hoặc tạo từ `.env.example`) và bổ sung:

```ini
# Telegram Integration Settings
TELEGRAM_BOT_TOKEN=7123456789:AAFxxx_your_real_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789
```

*Lưu ý*: Nếu muốn cho phép nhiều người dùng Telegram truy cập, điền danh sách phân tách bằng dấu phẩy: `TELEGRAM_ALLOWED_USERS=123456789,987654321`.

---

## 🚀 3. HƯỚNG DẪN KHỞI CHẠY BOT TRÊN LOCALHOST (POLLING MODE)

Nhờ có phân hệ **Telegram Long Polling Service**, bạn có thể test trực tiếp bot Telegram thật ngay trên máy tính local mà **KHÔNG cần domain HTTPS hay ngrok**:

Mở **PowerShell** và chạy lệnh:

```powershell
cd C:\Users\MSi\.gemini\antigravity\scratch\aimos\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Khi server khởi chạy thành công, log hệ thống sẽ báo:
`[TELEGRAM POLLING] Starting Telegram Bot Long Polling loop...`

Bây giờ bot của bạn trên Telegram đã sẵn sàng nhận tin nhắn!

---

## 🧪 4. DANH SÁCH BÀI TEST THỦ CÔNG (MANUAL TEST CHECKLIST)

Hãy mở ứng dụng Telegram và nhắn tin trực tiếp tới Bot của bạn theo 7 bài test sau:

### 📋 TEST 1: Khởi động Bot
- **Gõ**: `/start`
- **Phản hồi kỳ vọng**: Bot chào mừng và giới thiệu hệ thống AIMOS.

---

### 📋 TEST 2: Xem danh sách lệnh
- **Gõ**: `/help`
- **Phản hồi kỳ vọng**: Bot hiển thị toàn bộ danh sách lệnh có sẵn (`/start`, `/help`, `/status`, `/agents`, `/products`, `/research`).

---

### 📋 TEST 3: Kiểm tra trạng thái máy chủ AIMOS
- **Gõ**: `/status`
- **Phản hồi kỳ vọng**: Bot thông báo AIMOS Backend `v0.8.1` đang ở trạng thái Hoạt động bình thường (OK) với 7 AI Agent sẵn sàng.

---

### 📋 TEST 4: Xem danh sách AI Agents
- **Gõ**: `/agents`
- **Phản hồi kỳ vọng**: Bot trả về danh sách 7 AI Agents (`MarketResearchAgent`, `MarketingStrategyAgent`, `CreativeAgent`, `AdsAgent`, `OptimizationAgent`, `AutomationAgent`, `EcommerceAgent`).

---

### 📋 TEST 5: Luồng Nghiên cứu Thị trường Tương tác thoại (/research)
- **Bước 1 (Gõ)**: `/research`
  - *Bot trả lời*: `"📊 BẮT ĐẦU NGHIÊN CỨU THỊ TRƯỜNG. Bạn muốn nghiên cứu sản phẩm nào?"`
- **Bước 2 (Gõ)**: `Xe máy điện`
  - *Bot trả lời*: `"📦 Sản phẩm: Xe máy điện. Bạn muốn nghiên cứu tại thị trường nào?"`
- **Bước 3 (Gõ)**: `Vietnam`
  - *Bot trả lời*: Thông báo đang xử lý $\rightarrow$ Sau đó trả về **Báo cáo Phân tích chi tiết** từ `MarketResearchAgent (Provider: Mock)`!

---

### 📋 TEST 6: Thử nghiệm Tài khoản Không Được Phép (Unauthorized User)
- Cho một tài khoản Telegram khác (không nằm trong `TELEGRAM_ALLOWED_USERS`) nhắn `/start` hoặc `/research`.
- **Phản hồi kỳ vọng**: Bot từ chối thực thi và trả về thông báo:
  `⛔ TRUY CẬP BỊ TỪ CHỐI: Bạn không có quyền truy cập hệ thống AIMOS...`

---

### 📋 TEST 7: Kiểm tra Xử lý Lỗi Thân thiện (Error Handling)
- Khi hệ thống gặp sự cố backend, Bot sẽ không gửi stack trace mà trả về thông báo an toàn:
  `⚠️ AIMOS ERROR NOTICE: AIMOS gặp sự cố khi xử lý yêu cầu. Request ID: req_tg_xxx`

---

## 🌐 5. CHUYỂN ĐỔI SANG WEBHOOK TRONG MÔI TRƯỜNG PRODUCTION

Khi bạn triển khai AIMOS lên VPS/Cloud có domain HTTPS thật (Ví dụ: `https://api.yourdomain.com`), bạn có thể đăng ký Webhook với Telegram API bằng cách gọi curl:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://api.yourdomain.com/api/v1/telegram/webhook"
```

Endpoint kiểm tra trạng thái Telegram tích hợp:
- `GET /api/v1/integrations/telegram/status` (Hoặc `GET /api/v1/telegram/status`).
