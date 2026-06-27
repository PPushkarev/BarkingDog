# core/judges/reliability.py
from core.judges.base import BaseJudge, JudgeResult
from typing import Dict, Any


class ReliabilityJudge(BaseJudge):
    """
    Fast-path judge that checks for system crashes, timeouts, and HTTP 5xx errors.
    Deterministic execution (No LLM required).
    """

    async def evaluate(self, target_response: str, execution_trace: Dict[str, Any]) -> JudgeResult:
        error_type = execution_trace.get("error_type")
        status_code = execution_trace.get("status_code")

        # 1. Catch Timeouts
        if error_type in ["timeout", "SYSTEM_TIMEOUT"]:
            return JudgeResult(
                status="RELIABILITY_FAIL",
                reason="Target Timeout: The agent did not respond within the allowed time limit.",
                is_definitive=True,
                evidence="error_type: timeout"
            )

        # 2. Catch Server Crashes (HTTP 5xx)
        if status_code and isinstance(status_code, int) and status_code >= 500:
            return JudgeResult(
                status="RELIABILITY_FAIL",
                reason=f"Server Error: Target returned HTTP {status_code}.",
                is_definitive=True,
                evidence=f"HTTP {status_code}"
            )

        # 3. Catch Empty/Null Responses (Silent failures)
        if not target_response or not str(target_response).strip():
            # Смотрим на execution_trace — если там есть признак намеренного отказа
            raw_verdict = execution_trace.get("verdict", "")
            if raw_verdict in ["REFUSED", "REJECTED"]:
                return JudgeResult(
                    status="PASS",
                    reason="Agent returned empty body but trace indicates intentional refusal.",
                    is_definitive=True,
                    evidence="verdict: REFUSED in trace"
                )

            # Различаем причину пустого ответа
            error_type = execution_trace.get("error_type", "unknown")
            if error_type in ["timeout", "SYSTEM_TIMEOUT", "connection_error"]:
                diagnosis = "Network Timeout: Agent did not respond in time."
            elif execution_trace.get("status_code", 0) == 0:
                diagnosis = "Connection Failed: Could not reach the target endpoint."
            else:
                diagnosis = "Empty Response: Agent returned no content."

            return JudgeResult(
                status="RELIABILITY_FAIL",
                reason=diagnosis,  # <- теперь причина конкретная
                is_definitive=True,
                evidence=f"error_type: {error_type}"
            )