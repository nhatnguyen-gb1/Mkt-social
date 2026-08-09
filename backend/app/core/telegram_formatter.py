from typing import Dict, Any, List


class TelegramFormatter:
    """
    Dedicated Formatter for Telegram Bot Messages.
    Formats rich markdown responses with emojis and clear layout.
    """

    @staticmethod
    def format_welcome() -> str:
        return (
            "🤖 *AIMOS — AI Marketing Operating System*\n\n"
            "Xin chào! Tôi là trợ lý AI Marketing thông minh của AIMOS.\n"
            "Tôi có thể giúp bạn phân tích thị trường, lập chiến lược, tạo nội dung và tối ưu quảng cáo.\n\n"
            "Gõ `/help` để xem danh sách các lệnh điều khiển."
        )

    @staticmethod
    def format_help() -> str:
        return (
            "📌 *AIMOS TELEGRAM COMMANDS*\n\n"
            "• `/start` — Giới thiệu hệ thống AIMOS\n"
            "• `/help` — Danh sách các lệnh điều khiển\n"
            "• `/status` — Kiểm tra trạng thái máy chủ Backend\n"
            "• `/agents` — Xem danh sách các AI Agent hiện có\n"
            "• `/products` — Xem danh sách sản phẩm trong hệ thống\n"
            "• `/research` — Bắt đầu luồng Nghiên cứu thị trường\n\n"
            "💡 *Mẹo*: Bạn cũng có thể nhắn tin tự nhiên (Ví dụ: _\"Nghiên cứu xe máy điện tại Việt Nam\"_)."
        )

    @staticmethod
    def format_status(status_info: Dict[str, Any]) -> str:
        version = status_info.get("version", "0.8.1")
        env = status_info.get("environment", "development")
        agents_count = status_info.get("agents_count", 7)
        return (
            "🟢 *AIMOS SYSTEM STATUS*\n\n"
            f"• *Hệ thống*: AIMOS Backend Server\n"
            f"• *Phiên bản*: `v{version}`\n"
            f"• *Môi trường*: `{env}`\n"
            f"• *Trạng thái*: Hoạt động bình thường (OK)\n"
            f"• *Số lượng AI Agent*: {agents_count} Agents sẵn sàng\n"
        )

    @staticmethod
    def format_agents(agents_list: List[Dict[str, Any]]) -> str:
        msg = "🤖 *DANH SÁCH AI AGENT HIỆN CÓ*\n\n"
        for idx, ag in enumerate(agents_list, 1):
            name = ag.get("agent_name", "Agent")
            domain = ag.get("domain", "GENERAL")
            status = ag.get("status", "REAL")
            desc = ag.get("description", "")
            badge = "✅ REAL" if status == "REAL" else "🛠️ SKELETON"
            msg += f"*{idx}. {name}* `[{badge}]`\n"
            msg += f"   • Lĩnh vực: `{domain}`\n"
            msg += f"   • Mô tả: {desc}\n\n"
        return msg

    @staticmethod
    def format_products(products_list: List[Dict[str, Any]]) -> str:
        if not products_list:
            return (
                "📦 *DANH SÁCH SẢN PHẨM*\n\n"
                "Chưa có sản phẩm nào trong hệ thống.\n"
                "Bạn có thể tạo sản phẩm mới bằng API `POST /api/v1/products`."
            )
        msg = f"📦 *DANH SÁCH SẢN PHẨM ({len(products_list)})*\n\n"
        for idx, p in enumerate(products_list[:10], 1):
            name = p.get("name", "N/A")
            price = p.get("price", 0.0)
            sku = p.get("sku", "N/A")
            msg += f"*{idx}. {name}*\n"
            msg += f"   • Mã SKU: `{sku}` | Giá: ${price}\n\n"
        return msg

    @staticmethod
    def format_research_result(
        result: Dict[str, Any],
        provider_name: str = "mock",
        execution_time_ms: int = 0,
        request_id: str = "req_default",
    ) -> str:
        product_name = result.get("product_name", "N/A")
        target_market = result.get("target_market", "N/A")
        summary = result.get("summary", "Không có tóm tắt.")
        opps = result.get("opportunities", [])
        risks = result.get("risks", [])
        angles = result.get("recommended_marketing_angles", [])

        msg = (
            "📊 *AIMOS MARKET RESEARCH RESULT*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 *Sản phẩm*: {product_name}\n"
            f"🌍 *Thị trường*: {target_market}\n"
            f"⚙️ *Provider*: `{provider_name.upper()}`\n"
            f"⏱️ *Thời gian xử lý*: {execution_time_ms} ms\n"
            f"🆔 *Request ID*: `{request_id}`\n\n"
            f"📝 *Tóm tắt Phân tích*:\n{summary}\n\n"
        )

        if opps:
            msg += "💡 *Cơ hội phát triển*:\n"
            for op in opps:
                msg += f"  • {op}\n"
            msg += "\n"

        if risks:
            msg += "⚠️ *Rủi ro & Thách thức*:\n"
            for r in risks:
                msg += f"  • {r}\n"
            msg += "\n"

        if angles:
            msg += "🎯 *Góc độ Tiếp thị Đề xuất*:\n"
            for a in angles:
                msg += f"  • {a}\n"
            msg += "\n"

        msg += "✅ *Trạng thái*: Hoàn tất (Completed)"
        return msg

    @staticmethod
    def format_unauthorized(user_id: int) -> str:
        return (
            "⛔ *TRUY CẬP BỊ TỪ CHỐI*\n\n"
            f"Bạn không có quyền truy cập hệ thống AIMOS. Tài khoản Telegram của bạn (`ID: {user_id}`) không nằm trong danh sách Whitelist.\n\n"
            "Vui lòng liên hệ Quản trị viên để bổ sung ID của bạn vào `TELEGRAM_ALLOWED_USER_IDS`."
        )

    @staticmethod
    def format_error(error_msg: str, request_id: str = "req_error") -> str:
        return (
            "⚠️ *AIMOS ERROR NOTICE*\n\n"
            "AIMOS gặp sự cố khi xử lý yêu cầu của bạn.\n"
            f"• *Request ID*: `{request_id}`\n"
            f"• *Thông báo*: {error_msg}\n\n"
            "Chi tiết lỗi đã được ghi nhận trong nhật ký hệ thống."
        )
