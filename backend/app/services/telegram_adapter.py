import re
import uuid
import logging
from typing import Dict, Any, Optional
from app.core.telegram import TelegramClient
from app.core.telegram_formatter import TelegramFormatter
from app.services.telegram_auth_service import TelegramAuthService
from app.services.product_service import ProductService
from app.services.job_service import JobService
from app.services.agent_service import AgentService
from app.services.audit_service import AuditService
from app.schemas.agent import AgentResearchRequest
from app.schemas.product import ProductCreate
from app.schemas.job import JobCreate
from app.agents.registry import AgentRegistry

logger = logging.getLogger("aimos.telegram.adapter")


class TelegramAdapter:
    """
    Adapter for processing Telegram commands, interactive conversational state,
    and routing natural language requests to AIMOS application services.
    """

    # In-memory conversational state per user: {user_id: {"state": "...", "data": {...}}}
    _user_states: Dict[int, Dict[str, Any]] = {}

    def __init__(
        self,
        telegram_client: TelegramClient,
        auth_service: TelegramAuthService,
        product_service: ProductService,
        job_service: JobService,
        audit_service: AuditService,
        agent_service: Optional[AgentService] = None,
    ):
        self.telegram_client = telegram_client
        self.auth_service = auth_service
        self.product_service = product_service
        self.job_service = job_service
        self.audit_service = audit_service
        self.agent_service = agent_service

    async def handle_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process_update to preserve backward compatibility"""
        return await self.process_update(update)

    async def process_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for handling raw Telegram Update payloads (polling or webhook).
        """
        message = update.get("message") or update.get("edited_message")
        if not message:
            return {"status": "ignored", "reason": "No message payload"}

        chat_id = message.get("chat", {}).get("id")
        user = message.get("from", {})
        user_id = user.get("id")
        text = (message.get("text") or "").strip()

        request_id = f"req_tg_{uuid.uuid4().hex[:8]}"

        logger.info(
            f"[TELEGRAM INBOUND] update_id={update.get('update_id')} | user_id={user_id} | chat_id={chat_id} | text='{text}' | request_id={request_id}"
        )

        if not user_id or not chat_id:
            logger.warning(f"[TELEGRAM INBOUND IGNORED] Missing user_id ({user_id}) or chat_id ({chat_id})")
            return {"status": "ignored", "reason": "Missing user_id or chat_id"}

        # 1. User Authorization Check (Whitelist Guard)
        is_allowed = await self.auth_service.is_user_allowed(
            telegram_user_id=user_id,
            username=user.get("username"),
            first_name=user.get("first_name"),
        )

        logger.info(f"[TELEGRAM AUTH] user_id={user_id} | whitelist_allowed={is_allowed}")

        if not is_allowed:
            logger.warning(f"[TELEGRAM BLOCKED] Unauthorized access attempt by user_id={user_id}")
            unauth_msg = TelegramFormatter.format_unauthorized(user_id)
            await self.telegram_client.send_message(chat_id=chat_id, text=unauth_msg, parse_mode="Markdown")
            return {"status": "unauthorized", "user_id": user_id, "text": unauth_msg}

        # 2. Command / Message Routing
        try:
            if text.startswith("/"):
                logger.info(f"[TELEGRAM ROUTER] Routing command '{text.split()[0]}' for user_id={user_id}")
                return await self._handle_command(chat_id, user_id, text, request_id)
            else:
                logger.info(f"[TELEGRAM ROUTER] Routing natural language message for user_id={user_id}")
                return await self._handle_natural_language(chat_id, user_id, text, request_id)
        except Exception as exc:
            logger.error(f"❌ [TELEGRAM ROUTER ERROR] Exception processing text '{text}': {exc}", exc_info=True)
            error_reply = TelegramFormatter.format_error(
                error_msg="Hệ thống gặp sự cố khi xử lý yêu cầu.", request_id=request_id
            )
            await self.telegram_client.send_message(chat_id=chat_id, text=error_reply, parse_mode="Markdown")
            return {"status": "error", "request_id": request_id, "error": str(exc), "text": error_reply}

    async def _handle_command(
        self, chat_id: int, user_id: int, command_text: str, request_id: str
    ) -> Dict[str, Any]:
        parts = command_text.split()
        command = parts[0].lower().split("@")[0]

        # Reset conversational state on any command
        if user_id in self._user_states:
            del self._user_states[user_id]

        if command == "/start":
            reply = TelegramFormatter.format_welcome()
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/start", "text": reply}

        elif command == "/help":
            reply = TelegramFormatter.format_help()
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/help", "text": reply}

        elif command == "/status":
            status_data = {
                "system": "AIMOS Backend",
                "version": "0.8.1",
                "environment": "development",
                "agents_count": len(AgentRegistry.list_all_agents()),
            }
            reply = TelegramFormatter.format_status(status_data)
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/status", "text": reply}

        elif command == "/agents":
            agents_list = AgentRegistry.list_all_agents()
            reply = TelegramFormatter.format_agents(agents_list)
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/agents", "text": reply}

        elif command == "/products" or command == "/list_products":
            products_res = await self.product_service.list_products()
            if hasattr(products_res, "items"):
                items = products_res.items
            elif isinstance(products_res, (list, tuple)):
                items = products_res[0] if isinstance(products_res, tuple) else products_res
            else:
                items = []
            products_dict = [p.model_dump() if hasattr(p, "model_dump") else p for p in items]
            reply = TelegramFormatter.format_products(products_dict)
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": command, "text": reply}

        elif command == "/create_product":
            product_name = " ".join(parts[1:]) if len(parts) > 1 else "Sản phẩm Telegram Mới"
            prod = await self.product_service.create_product(
                ProductCreate(name=product_name, price=99.9, category="Telegram")
            )
            reply = f"Đã tạo sản phẩm thành công trên AIMOS!\n• Tên: {prod.name}\n• ID: {prod.id}"
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/create_product", "product_id": str(prod.id), "text": reply}

        elif command == "/run_job":
            job_type = parts[1] if len(parts) > 1 else "MARKET_RESEARCH"
            job = await self.job_service.create_job(
                JobCreate(name=f"Job {job_type}", job_type=job_type, payload={"source": "telegram"})
            )
            reply = f"Đã tạo nhiệm vụ ngầm thành công!\n• Mã Job: {job.id}\n• Loại: {job.job_type}"
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/run_job", "job_id": str(job.id), "text": reply}

        elif command == "/research":
            # Initiate Interactive Research Conversation
            self._user_states[user_id] = {"state": "AWAITING_PRODUCT", "data": {}}
            reply = (
                "📊 *BẮT ĐẦU NGHIÊN CỨU THỊ TRƯỜNG*\n\n"
                "Bạn muốn nghiên cứu sản phẩm nào?\n"
                "_(Ví dụ nhập: Xe máy điện, Bánh Trung Thu, Mỹ phẩm)_"
            )
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "success", "command": "/research", "state": "AWAITING_PRODUCT", "text": reply}

        else:
            reply = (
                f"❓ Không nhận diện được lệnh `{command}`.\n"
                "Gõ `/help` để xem danh sách các lệnh hỗ trợ."
            )
            await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
            return {"status": "unknown_command", "command": command, "text": reply}

    async def _handle_natural_language(
        self, chat_id: int, user_id: int, text: str, request_id: str
    ) -> Dict[str, Any]:
        user_state = self._user_states.get(user_id)

        # 1. Handle Conversational State Machine for /research
        if user_state:
            curr_state = user_state.get("state")
            data = user_state.get("data", {})

            if curr_state == "AWAITING_PRODUCT":
                data["product_name"] = text
                self._user_states[user_id] = {"state": "AWAITING_MARKET", "data": data}
                reply = (
                    f"📦 Sản phẩm: *{text}*\n\n"
                    "🌍 Bạn muốn nghiên cứu tại thị trường nào?\n"
                    "_(Ví dụ nhập: Vietnam, Global, Southeast Asia)_"
                )
                await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
                return {"status": "in_progress", "state": "AWAITING_MARKET", "text": reply}

            elif curr_state == "AWAITING_MARKET":
                product_name = data.get("product_name", text)
                target_market = text
                del self._user_states[user_id]

                prog_reply = f"⏳ *AIMOS đang chạy MarketResearchAgent (Provider: Mock)...*\nSản phẩm: `{product_name}` | Thị trường: `{target_market}`"
                await self.telegram_client.send_message(chat_id=chat_id, text=prog_reply, parse_mode="Markdown")

                return await self._execute_research(
                    chat_id=chat_id,
                    user_id=user_id,
                    product_name=product_name,
                    target_market=target_market,
                    request_id=request_id,
                )

        # 2. One-Shot / Heuristic Intent Extraction from Natural Language
        lower_text = text.lower()
        if any(kw in lower_text for kw in ["nghiên cứu", "tìm hiểu", "phân tích"]):
            extracted_prod, extracted_market = self._extract_research_params(text)
            
            if extracted_prod:
                prog_reply = f"⏳ *AIMOS đang chạy MarketResearchAgent (Provider: Mock)...*\nSản phẩm: `{extracted_prod}` | Thị trường: `{extracted_market}`"
                await self.telegram_client.send_message(chat_id=chat_id, text=prog_reply, parse_mode="Markdown")

                return await self._execute_research(
                    chat_id=chat_id,
                    user_id=user_id,
                    product_name=extracted_prod,
                    target_market=extracted_market,
                    request_id=request_id,
                )
            else:
                self._user_states[user_id] = {"state": "AWAITING_PRODUCT", "data": {}}
                reply = (
                    f"📊 Tôi nhận thấy bạn muốn nghiên cứu thị trường cho: *\"{text[:50]}\"*\n\n"
                    "Bạn muốn chỉ định chính xác tên sản phẩm nào?"
                )
                await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
                return {"status": "in_progress", "state": "AWAITING_PRODUCT", "text": reply}

        # Default Fallback Guidance
        reply = (
            f"💡 Hướng dẫn: Bạn vừa nhập _\"{text[:40]}\"_\n\n"
            "Để khởi chạy quy trình AI, vui lòng chọn một trong các lệnh sau:\n"
            "• `/research` — Bắt đầu nghiên cứu sản phẩm mới\n"
            "• `/agents` — Xem danh sách các AI Agent sẵn sàng\n"
            "• `/help` — Xem hướng dẫn chi tiết"
        )
        await self.telegram_client.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
        return {"status": "fallback_guidance", "text": reply}

    def _extract_research_params(self, text: str) -> tuple[Optional[str], str]:
        """Extracts product_name and target_market from natural language text"""
        lower = text.lower()
        target_market = "Vietnam" if ("việt nam" in lower or "vietnam" in lower) else "Global"
        product_name = None

        # 1. Match "sản phẩm X", "về X", "cho X"
        match = re.search(r"(?:sản phẩm|về|cho)\s+([^\.\,\;\n]+)", text, re.IGNORECASE)
        if match:
            raw_prod = match.group(1).strip()
            raw_prod = re.sub(r"\s+tại\s+thị\s+trường.*$", "", raw_prod, flags=re.IGNORECASE).strip()
            raw_prod = re.sub(r"\s+tại\s+việt\s+nam.*$", "", raw_prod, flags=re.IGNORECASE).strip()
            raw_prod = re.sub(r"\s+tại\s+vietnam.*$", "", raw_prod, flags=re.IGNORECASE).strip()
            raw_prod = re.sub(r"\s+phân\s+tích.*$", "", raw_prod, flags=re.IGNORECASE).strip()
            if len(raw_prod) > 1:
                product_name = raw_prod.title()

        # 2. Match text after "nghiên cứu X" or "tìm hiểu X" or "phân tích X"
        if not product_name:
            match_verb = re.search(r"(?:nghiên cứu|tìm hiểu|phân tích|đánh giá)\s+([^\.\,\;\n]+)", text, re.IGNORECASE)
            if match_verb:
                raw_prod = match_verb.group(1).strip()
                raw_prod = re.sub(r"\s+tại\s+thị\s+trường.*$", "", raw_prod, flags=re.IGNORECASE).strip()
                raw_prod = re.sub(r"\s+tại\s+việt\s+nam.*$", "", raw_prod, flags=re.IGNORECASE).strip()
                raw_prod = re.sub(r"\s+tại\s+vietnam.*$", "", raw_prod, flags=re.IGNORECASE).strip()
                raw_prod = re.sub(r"\s+phân\s+tích.*$", "", raw_prod, flags=re.IGNORECASE).strip()
                if len(raw_prod) > 1:
                    product_name = raw_prod.title()

        return product_name, target_market

    async def _execute_research(
        self, chat_id: int, user_id: int, product_name: str, target_market: str, request_id: str
    ) -> Dict[str, Any]:
        if not self.agent_service:
            err_msg = TelegramFormatter.format_error("AgentService chưa được kết nối.", request_id)
            await self.telegram_client.send_message(chat_id=chat_id, text=err_msg, parse_mode="Markdown")
            return {"status": "error", "reason": "AgentService missing"}

        try:
            req = AgentResearchRequest(
                product_name=product_name,
                target_market=target_market,
                provider="mock",
            )
            agent_run = await self.agent_service.run_market_research(req, actor_id=str(user_id))

            formatted_reply = TelegramFormatter.format_research_result(
                result=agent_run.result or {},
                provider_name=agent_run.provider_used or "mock",
                execution_time_ms=agent_run.execution_time_ms or 0,
                request_id=request_id,
            )

            await self.telegram_client.send_message(chat_id=chat_id, text=formatted_reply, parse_mode="Markdown")

            return {
                "status": "success",
                "action": "research_completed",
                "request_id": request_id,
                "agent_run_id": str(agent_run.run_id),
                "text": formatted_reply,
            }
        except Exception as exc:
            logger.error(f"[TELEGRAM AGENT ERROR] {exc}", exc_info=True)
            err_reply = TelegramFormatter.format_error("Lỗi khi thực thi MarketResearchAgent.", request_id)
            await self.telegram_client.send_message(chat_id=chat_id, text=err_reply, parse_mode="Markdown")
            return {"status": "error", "request_id": request_id, "error": str(exc), "text": err_reply}
