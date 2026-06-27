# core/judges/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class JudgeResult(BaseModel):
    """
    Standardized output for all judges in the ensemble, now supporting UNCERTAIN state.
    """
    status: str             # "PASS", "SECURITY_FAIL", "RELIABILITY_FAIL", "UNCERTAIN"
    reason: str             # Explanation of the verdict
    is_definitive: bool     # True if it safely shorts the execution pipeline
    confidence: float = 1.0
    evidence: Optional[str] = None


class BaseJudge(ABC):
    """
    Abstract base class for all security and reliability judges.
    """

    @abstractmethod
    async def evaluate(self, target_response: str, execution_trace: Dict[str, Any]) -> JudgeResult:
        """
        Evaluates the target's response.

        Args:
            target_response: The raw text response from the agent.
            execution_trace: Metadata like HTTP status codes, timeouts, or tool call traces.

        Returns:
            A JudgeResult object containing the verdict.
        """
        pass