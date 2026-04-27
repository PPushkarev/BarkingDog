# core/delivery.py
"""
Handles delivery of completed scan reports to external notification channels.

Currently supports Telegram: sends a Markdown summary message followed by
the full HTML report as a file attachment. Requires TELEGRAM_BOT_TOKEN and
TELEGRAM_CHAT_ID to be set in the environment.
"""

# =============================================================================
# Score thresholds used to pick the status icon in the Telegram message
# =============================================================================
SCORE_ICON_HIGH = "🟢"   # score >= 90
SCORE_ICON_MID  = "🟡"   # score >= 70
SCORE_ICON_LOW  = "🔴"   # score <  70

# =============================================================================
# Built-in
# =============================================================================
import os

# =============================================================================
# Third-party
# =============================================================================
import httpx

# =============================================================================
# Local
# =============================================================================
from core.schemas import ReportSummary


class TelegramDelivery:
    """Delivers scan reports to a Telegram chat via the Bot API."""

    @staticmethod
    async def send_report(report: ReportSummary, html_path: str) -> None:
        """
        Sends a Markdown summary message and the HTML report file to Telegram.

        Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from the environment.
        Silently skips delivery if either credential is missing.

        Two sequential API calls are made:
          1. sendMessage  — posts the text summary with score and stress stats.
          2. sendDocument — uploads the HTML report as a file attachment.

        Args:
            report:    Completed ReportSummary containing scores and statistics.
            html_path: Absolute or relative path to the generated HTML report file.

        Returns:
            None
        """
        token   = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            print("⚠️ [DELIVERY] Telegram credentials not found in .env. Skipping alert.")
            return

        print("📡 [DELIVERY] Sending report to Telegram...")

        # Pick status icon based on score thresholds
        status_icon = (
            SCORE_ICON_HIGH if report.score >= 90
            else (SCORE_ICON_MID if report.score >= 70 else SCORE_ICON_LOW)
        )
        stress_icon = (
            "✅" if (report.stress_test and report.stress_test.failed_count == 0)
            else "❌"
        )

        text  = "🐶 *BarkingDog Agent Report*\n\n"
        text += f"🎯 *Target:* `{report.target_url}`\n"
        text += f"{status_icon} *Logic Score:* {report.score}/100\n"
        text += f"🛡️ *Vulnerabilities:* {report.vulnerabilities_found}/{report.total_tests}\n"

        if report.stress_test:
            text += f"\n🌊 *DDoS Test:* {stress_icon}\n"
            text += f"   • Success: {report.stress_test.success_count}\n"
            text += f"   • Failed: {report.stress_test.failed_count}\n"
            text += f"   • Speed: {report.stress_test.req_per_sec} req/s\n"

        # Step 1: send the text summary
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient(trust_env=False) as client:
            await client.post(
                api_url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )

        # Step 2: upload the HTML report as a file attachment
        doc_url = f"https://api.telegram.org/bot{token}/sendDocument"
        async with httpx.AsyncClient(trust_env=False) as client:
            with open(html_path, "rb") as f:
                await client.post(doc_url, data={"chat_id": chat_id}, files={"document": f})

        print("✅ [DELIVERY] Successfully sent to Telegram.")