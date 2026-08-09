# MARKETING LEAD AGENT: GITHUB OPEN SOURCE ARCHITECTURE REVIEW & COMPARISON REPORT

Báo cáo nghiên cứu, đối chiếu và đề xuất cải tiến cho **Marketing Lead Agent V1** dựa trên 4 dự án nguồn mở hàng đầu:
1. `agentskills/agentskills` (Open Standard Spec cho AI Agent Skills)
2. `coreyhaines31/marketingskills` (Thư viện Skill Tiếp thị thực chiến cho AI Agent)
3. `whyashthakker/agent-skills-marketing` (Bộ 50+ Marketing Skills cho AI Agent)
4. `openai/openai-agents-python` (Khung đa tác vụ Multi-Agent Orchestration, Handoff & Guardrails)

---

## 📌 1. CURRENT AIMOS IMPLEMENTATION (THỰC TRẠNG AIMOS V1)
- **Cấu trúc Hồ sơ Agent (`agents/marketing_lead/`)**: Phân tách file `ROLE.md`, `MISSION.md`, `KNOWLEDGE/`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`, `TOOLS.md`, `PERMISSIONS.md`.
- **Hệ thống Skill (Skill System V1)**: Đã có 25 Skills chuẩn hóa (mỗi skill gồm `SKILL.md`, `RULES.md`, `EXAMPLES.md`, `EVALS.md`).
- **Luồng Điều phối (Orchestration)**: `MarketingLeadAgent` lập Task Plan, chọn Sub-agent (`MarketResearchAgent`, `MarketingStrategyAgent`, `CreativeAgent`, `AdsAgent`, `OptimizationAgent`), kiểm tra trạng thái (hỗ trợ báo `"Agent unavailable"`), thực thi `Output Review Framework` (0-100 score, ACCEPT/REJECT) và tổng hợp phân tách `Fact / Inference / Assumption / Unknown / Recommendation`.
- **API & REST**: Route `POST /api/v1/agents/marketing-lead/analyze` và test suite 70/70 test cases Passed 100%.

---

## 📚 2. GITHUB REFERENCES OVERVIEW (TỔNG QUAN TÀI LIỆU THAM KHẢO)

### A. `agentskills/agentskills` (Open Specification)
- **Tôn chỉ**: Đơn giản, di động, không bị khóa chặt vào một vendor (Portable Markdown-based Agent Skill Standard).
- **Điểm cốt lõi**:
  - `Progressive Disclosure`: Ban đầu AI chỉ nạp `name` + `description` để tiết kiệm Context Window. Khi cần mới nạp toàn bộ body `SKILL.md`.
  - Directory Structure chuẩn: `skill-name/SKILL.md` kèm tùy chọn `scripts/`, `references/`, `assets/`.
  - YAML Frontmatter chuẩn: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.

### B. `coreyhaines31/marketingskills` & `whyashthakker/agent-skills-marketing`
- **Tôn chỉ**: Cung cấp tri thức tiếp thị thực chiến chuẩn hóa thay vì prompt chung chung.
- **Điểm cốt lõi**:
  - **Single Source of Truth (`product-marketing.md`)**: Tất cả các skill tiếp thị (SEO, Copywriting, Ads) đều đối chiếu lại tài liệu trung tâm này để không lệch định vị thương hiệu.
  - **Phân khúc chuyên biệt**: Phân chia theo Funnel (Acquisition, Activation, Revenue, Retention, Referral) và các chiến thuật hiện đại (GEO - Generative Engine Optimization, Cold Email, CRO - Conversion Rate Optimization, Viral Loops).

### C. `openai/openai-agents-python` (Agent Orchestration Framework)
- **Tôn chỉ**: Khung điều phối Multi-agent sản xuất nhẹ nhàng, đáng tin cậy.
- **Điểm cốt lõi**:
  - **Explicit Handoff Objects**: Chuyển giao tác vụ giữa Orchestrator và Specialist Agents bằng đối tượng Handoff rõ ràng.
  - **Input/Output Guardrails**: Kiểm soát tính hợp lệ của câu lệnh người dùng (Input Guardrail) và kết quả câu trả lời của Agent (Output Guardrail) trước khi trả về.
  - **Tracing & Observability**: Theo dõi cây vết thực thi của từng Agent và Tool call.

---

## 🌟 3. WHAT AIMOS ALREADY DOES WELL (ĐIỂM AIMOS ĐÃ LÀM TỐT)
1. **Kiến trúc Skill System chuẩn hóa 100% Native**: AIMOS đã có sẵn `SkillLoader`, `SkillRegistry`, `SkillExecutor` và `SkillEvaluator` đọc trực tiếp từ thư mục `backend/skills/` mà không cần n8n hay thư viện bên thứ 3.
2. **Output Review Framework sắc bén**: Đánh giá kết quả làm việc của Sub-agents theo 6 tiêu chí (Accuracy, Completeness, Relevance, Evidence, Business Impact, Rule Compliance) với điểm ngưỡng configurable (ACCEPT / REJECT) - vượt trội so với các prompt đơn giản trên GitHub.
3. **Phân tách dữ liệu minh bạch (Decision Making Guard)**: Phân rành mạch `Fact / Inference / Assumption / Unknown / Recommendation`, ngăn chặn tuyệt đối việc AI bịa đặt dữ liệu (Hallucination) hoặc biến giả định thành sự thật.
4. **Phân quyền rủi ro (PERMISSIONS.md)**: Chặn tuyệt đối hành vi tự ý tiêu tiền thật hoặc xuất bản Ads chưa có Human Approval.

---

## ⚠️ 4. WHAT AIMOS IS MISSING (NHỮNG PHẦN AIMOS ĐANG THIẾU)
1. **Thiếu Single Source of Truth (`product_marketing_context`)**: AIMOS hiện chưa có cơ chế gom toàn bộ bối cảnh thương hiệu (Brand Positioning, Persona, Value Proposition) thành 1 nguồn tri thức trung tâm để tất cả các Skill cùng truy vấn.
2. **Thiếu cơ chế Progressive Disclosure**: Hiện tại AIMOS nạp toàn bộ thông tin Skill vào RAM khi khởi động thay vì nạp lười (Lazy Load Metadata trước, Load Body khi thực thi) dẫn đến tốn Context Window khi mở rộng hàng trăm Skill.
3. **Thiếu các Skill Tiếp thị Hiện đại (GEO / CRO / Copywriting / Churn / Referral)**: Danh sách Skill hiện tại mới tập trung vào khung quản lý tổng quan, chưa có các chiến thuật tiếp thị 2026 như Generative Engine Optimization (GEO), Conversion Rate Optimization (CRO), Cold Email, Viral Loops.
4. **Thiếu Input & Output Guardrails độc lập**: Output Review hiện mới chạy ở cấp Sub-agent, chưa có Input Guardrail bảo vệ Marketing Lead trước các prompt chứa rủi ro hoặc không hợp lệ.

---

## 🚀 5. RECOMMENDED IMPROVEMENTS (ĐỀ XUẤT CẢI TIẾN)

### A. Skills khuyến nghị bổ sung/adapt:
1. `product_marketing_context` (Cảm hứng: `coreyhaines31/marketingskills`): Skill khởi tạo Nguồn tri thức Trung tâm về Thương hiệu & Sản phẩm.
2. `generative_engine_optimization` (Cảm hứng: `coreyhaines31/marketingskills`): Skill tối ưu sự xuất hiện của sản phẩm trên các công cụ tìm kiếm AI (Gemini, Perplexity, ChatGPT).
3. `conversion_rate_optimization` (Cảm hứng: `coreyhaines31/marketingskills`): Skill tối ưu tỷ lệ chuyển đổi Landing Page & Checkout.
4. `viral_referral_loop` (Cảm hứng: `whyashthakker/agent-skills-marketing`): Skill thiết kế vòng lặp giới thiệu lan truyền (Referral & Viral Growth).
5. `retention_churn_prevention` (Cảm hứng: `coreyhaines31/marketingskills`): Skill chăm sóc giữ chân & chống rời bỏ khách hàng.

### B. Tri thức (Knowledge) khuyến nghị bổ sung:
- Bổ sung `geo_search_optimization.md` và `cro_conversion_framework.md` vào `backend/agents/marketing_lead/KNOWLEDGE/`.

### C. Quy tắc (Rules) khuyến nghị bổ sung:
- Thêm quy tắc **Single Source of Truth**: Tất cả chiến lược tiếp thị phải đối chiếu với `product_marketing_context` trước khi lập kế hoạch.
- Thêm quy tắc **Progressive Context Disclosure**: Chỉ nạp chi tiết Skill khi được kích hoạt thực thi.

### D. Kiến trúc & Bảo mật (Architecture & License):
- Áp dụng cơ chế **Progressive Disclosure** (Metadata-first loading) theo chuẩn `agentskills/agentskills`.
- Áp dụng **Input Guardrail** theo mô hình `openai/openai-agents-python`.
- **License / Attribution**: Mọi Skill/Knowledge lấy cảm hứng từ GitHub sẽ được ghi nhận nguồn rõ ràng ở header comment (`Inspired by coreyhaines31/marketingskills, MIT License`).
