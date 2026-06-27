# core/agent/router.py
import logging
from typing import List, Dict, Any
from core.agent.schemas import AgentTestCase


class AgentRouter:
    """
    Execution mode dispatcher for BarkingDog.
    Separates the execution flow between classic chatbots and autonomous agents.
    """

    def __init__(self, mode: str = "bot"):
        self.mode = mode.lower()
        if self.mode not in ["bot", "agent", "rag", "compliance", "regression"]:
            logging.warning(f"[ROUTER] Unknown mode '{mode}', defaulting to 'bot'")
            self.mode = "bot"

    def filter_test_cases(self, all_cases: List[Any]) -> List[Any]:
        """
        Filters the input test cases based on the selected execution mode.

        Args:
            all_cases: A list containing both basic TestCase and AgentTestCase objects.
        Returns:
            A filtered list of test cases applicable to the current mode.
        """
        if self.mode == "agent":
            # Select only cases targeting agent infrastructure and tools
            return [
                c for c in all_cases
                if isinstance(c, AgentTestCase) or getattr(c, "owasp_asi", "").startswith("ASI")
            ]

        if self.mode == "bot":
            # Exclude specific agent cases (auth, MCP) for classic bots
            return [
                c for c in all_cases
                if not isinstance(c, AgentTestCase) and getattr(c, "category", "") != "excessive_agency"
            ]

        return all_cases

    def configure_execution_environment(self, test_case: Any) -> Dict[str, Any]:
        """
        Dynamically configures network headers and security context for the HTTP runner.

        Args:
            test_case: The current test case being evaluated.
        Returns:
            A dictionary containing HTTP headers and timeout settings.
        """
        env_config = {
            "headers": {
                "User-Agent": "BarkingDog-Agentic-Scanner/2.0",
                "Content-Type": "application/json"
            },
            "timeout": 45.0
        }

        # Inject authorization context if this is a Tenant Isolation test
        if hasattr(test_case, "auth_headers") and test_case.auth_headers:
            env_config["headers"].update(test_case.auth_headers)

        return env_config