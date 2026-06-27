
# # core/agent/transport.py
# import aiohttp
# import asyncio
# import logging
# from typing import Dict, Any
#
#
# class AgentTransport:
#     """
#     Handles real asynchronous HTTP communication with the target Agent webhooks.
#     """
#
#     @staticmethod
#     async def send_payload(url: str, payload: str, headers: Dict[str, str] = None) -> str:
#         """
#         Sends the attack payload to the target agent API via a POST request.
#         """
#         request_headers = {"Content-Type": "application/json"}
#         if headers:
#             request_headers.update(headers)
#
#         # Standard payload structure.
#         data = {"message": payload}
#
#         try:
#             # Увеличиваем таймаут до 45 секунд (Railway часто долго просыпается)
#             timeout = aiohttp.ClientTimeout(total=45)
#
#             async with aiohttp.ClientSession(timeout=timeout) as session:
#                 async with session.post(url, json=data, headers=request_headers) as response:
#                     response_text = await response.text()
#
#                     if not response_text and response.status >= 400:
#                         return f"HTTP_{response.status}_ERROR"
#
#                     return response_text
#
#         except asyncio.TimeoutError:
#             logging.error("[TRANSPORT] Target server timed out (took >45s)")
#             raise Exception("Timeout: Railway target took too long to respond.")
#         except aiohttp.ClientError as e:
#             # Используем repr(e), чтобы всегда видеть класс ошибки, даже если она пустая
#             logging.error(f"[TRANSPORT] Network request failed: {repr(e)}")
#             raise Exception(f"HTTP Request failed: {repr(e)}")


# core/agent/transport.py
import aiohttp
import asyncio
import logging
from typing import Dict, Any, List


class AgentTransport:
    """
    Enterprise Transport Layer for asynchronous HTTP communication.
    Includes Exponential Backoff, self-DoS protection, and Context Smuggling support.
    """

    def __init__(self, timeout_seconds: int = 45, max_retries: int = 3):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.max_retries = max_retries

    async def send_payload(self, url: str, payload: str, headers: Dict[str, str],
                           history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Sends payload and context history to target. Never raises fatal exceptions.
        """
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        data = {
            "message": payload,
            "mode": "agent_audit",
            "chat_history": history or []
        }

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(url, json=data, headers=request_headers) as resp:
                        status = resp.status
                        raw_text = await resp.text()
                        headers_dump = dict(resp.headers)

                        if status >= 500:
                            if attempt < self.max_retries - 1:
                                logging.warning(
                                    f"⚠️ Target HTTP {status}. Retrying {attempt + 1}/{self.max_retries}...")
                                await asyncio.sleep(2 ** attempt)
                                continue
                            return {"type": "ERROR_RESPONSE", "status": status, "body": raw_text,
                                    "reason": "Server Crash"}

                        if not raw_text or len(raw_text.strip()) == 0:
                            if status in [401, 403]:
                                fallback_msg = f"[BLOCKED_BY_WAF] HTTP {status} Forbidden/Unauthorized. Payload dropped."
                                return {"type": "VALID_RESPONSE", "status": status, "body": fallback_msg,
                                        "headers": headers_dump}
                            else:
                                fallback_msg = f"[EMPTY_REPLY] HTTP {status}. Server accepted request but returned nothing."
                                return {"type": "VALID_RESPONSE", "status": status, "body": fallback_msg,
                                        "headers": headers_dump}
                        # -----------------------------------------------------------------

                        return {"type": "VALID_RESPONSE", "status": status, "body": raw_text, "headers": headers_dump}

            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logging.warning(f"⚠️ Target Timeout. Retrying {attempt + 1}/{self.max_retries}...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"type": "SYSTEM_TIMEOUT", "status": 408, "body": "", "reason": "Target Timeout"}

            except Exception as e:
                if attempt < self.max_retries - 1:
                    logging.warning(f"⚠️ Target Network Error ({e}). Retrying...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"type": "SYSTEM_ERROR", "status": 0, "body": str(e), "reason": "Network Failure"}