import random
import time
import httpx


class TelegramAdapter:
    """
    Оборачивает атаку BarkingDog в настоящий Telegram Update формат.
    Бот получает запрос точно так же как от реального пользователя.
    """

    FAKE_USER_ID = 777000001
    FAKE_CHAT_ID = 777000001

    def _build_update(self, text: str) -> dict:
        return {
            "update_id": random.randint(100_000_000, 999_999_999),
            "message": {
                "message_id": random.randint(1, 99999),
                "from": {
                    "id": self.FAKE_USER_ID,
                    "is_bot": False,
                    "first_name": "SecurityAudit",
                    "username": "barkingdog_scanner"
                },
                "chat": {
                    "id": self.FAKE_CHAT_ID,
                    "type": "private",
                    "first_name": "SecurityAudit"
                },
                "date": int(time.time()),
                "text": text
            }
        }

    def extract_reply(self, raw_response: dict | str) -> str:
        """
        Aiogram ничего не возвращает в теле ответа — он шлёт
        сообщение обратно через Telegram Bot API.
        Поэтому нам нужен отдельный capture-эндпоинт.
        """
        if isinstance(raw_response, dict):
            # Если твой бот всё-таки возвращает reply в теле
            return (
                raw_response.get("reply") or
                raw_response.get("text") or
                raw_response.get("message", {}).get("text", "") or
                str(raw_response)
            )
        return str(raw_response)

    async def send(
        self,
        client: httpx.AsyncClient,
        target_url: str,
        attack_prompt: str
    ) -> str:
        payload = self._build_update(attack_prompt)
        response = await client.post(target_url, json=payload)
        response.raise_for_status()
        return self.extract_reply(response.json())