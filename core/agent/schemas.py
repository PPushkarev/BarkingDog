# core/agent/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from core.schemas import TestCase, MultiTurnTestCase

# Mapping of attack strategies to OWASP Agentic Security (2026) standards
OWASP_ASI_MAP = {
    "goal_hijacking": "ASI01",         # Agent Goal Hijacking
    "tool_argument_inject": "ASI02",   # Tool Misuse & Recursive Execution
    "tenant_isolation": "ASI03",       # Identity & Privilege Abuse (Data Leak)
    "mcp_supply_chain": "ASI04",       # Model Context Protocol Dependency Risks
    "code_execution": "ASI05",         # Unexpected Actions / Agent RCE
    "context_poisoning": "ASI06",      # Stateful Context Poisoning
    "multi_agent_chaining": "ASI07",   # Insecure Inter-Agent Communication
    "cascading_failure": "ASI08",      # Agentic Denial of Service / Loops
    "crescendo": "LLM01",              # Legacy Prompt Injection
    "roleplay": "LLM01",               # Legacy Prompt Injection
}

class AgentTestCase(TestCase):
    """
    Extended TestCase class specifically for autonomous AI Agents.
    Includes support for authorization headers and tool execution constraints.
    """
    owasp_asi: str = Field(
        default="ASI01",
        description="OWASP Agentic Security ID (ASI01-ASI10)"
    )
    cisa_category: str = Field(
        default="behavioral_misalignment",
        description="CISA Risk Category for structured audit logging"
    )
    auth_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Auth tokens for multi-tenant isolation testing (e.g., Tenant A token)"
    )
    forbidden_tools: List[str] = Field(
        default_factory=list,
        description="List of tool names that must NEVER be triggered during this test"
    )
    forbidden_data: List[str] = Field(
        default_factory=list,
        description="Data strings (e.g., Tenant B UUIDs) that must NEVER appear in the response"
    )
    regex_patterns: List[str] = Field(
        default_factory=list,
        description="Regex patterns to deterministically catch exposed secrets (e.g., AWS keys, JWTs)"
    )
    expected_structure: Optional[str] = Field(
        default=None,
        description="Expected format of structural leaks (e.g., 'sql_schema', 'json_array')"
    )

class AgentMultiTurnTestCase(MultiTurnTestCase, AgentTestCase):
    """
    Stateful multi-turn attack scenario for AI Agents.
    Combines agent-specific constraints with conversation history.
    """
    session_id: Optional[str] = Field(
        default=None,
        description="Unique identifier to track stateful conversation context"
    )