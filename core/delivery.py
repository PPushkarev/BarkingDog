import os
import httpx
from core.schemas import ReportSummary


class TelegramDelivery:
    @staticmethod
    async def send_report(report: ReportSummary, html_path: str):
        """Sends a summary message and the HTML report document to Telegram."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            print("⚠️ [DELIVERY] Telegram credentials not found in .env. Skipping alert.")
            return

        print("📡 [DELIVERY] Sending report to Telegram...")

        status_icon = "🟢" if report.score >= 90 else ("🟡" if report.score >= 70 else "🔴")
        stress_icon = "✅" if (report.stress_test and report.stress_test.failed_count == 0) else "❌"

        text = f"🐶 *BarkingDog Agent Report*\n\n"
        text += f"🎯 *Target:* `{report.target_url}`\n"
        text += f"{status_icon} *Logic Score:* {report.score}/100\n"
        text += f"🛡️ *Vulnerabilities:* {report.vulnerabilities_found}/{report.total_tests}\n"

        if report.stress_test:
            text += f"\n🌊 *DDoS Test:* {stress_icon}\n"
            text += f"   • Success: {report.stress_test.success_count}\n"
            text += f"   • Failed: {report.stress_test.failed_count}\n"
            text += f"   • Speed: {report.stress_test.req_per_sec} req/s\n"

        # 1. Отправляем текст (Сводка)
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient(trust_env=False) as client:
            await client.post(api_url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

        # 2. Отправляем сам HTML-файл
        doc_url = f"https://api.telegram.org/bot{token}/sendDocument"
        async with httpx.AsyncClient(trust_env=False) as client:
            with open(html_path, "rb") as f:
                await client.post(doc_url, data={"chat_id": chat_id}, files={"document": f})

        print("✅ [DELIVERY] Successfully sent to Telegram.")