# core/schemas.py
"""
Pydantic data models for the BarkingDog security scanner.

Defines all shared data contracts used across the scan pipeline:
  - TestStatus      : enum of possible test outcomes
  - TestCase        : single-turn test definition
  - MultiTurnTestCase : multi-turn / crescendo test definition
  - AttackResult    : outcome of executing one test case
  - StressResult    : outcome of a stress / load test run
  - MultiTurnSummary: aggregated multi-turn statistics with computed ASR / BDR
  - ReportSummary   : top-level scan report containing all results and scores

Declaration order matters: AttackResult must be defined before ReportSummary
because ReportSummary holds a List[AttackResult].
"""

# =============================================================================
# Built-in
# =============================================================================
from enum import Enum
from typing import Dict, List, Optional

# =============================================================================
# Third-party
# =============================================================================
from pydantic import BaseModel, computed_field, model_validator

# =============================================================================
# Local
# (none)
# =============================================================================


# ── Enumerations ──────────────────────────────────────────────────────────────
# core/schemas.py — в начале файла добавь словарь

CATEGORY_OWASP_MAP = {
    "prompt_injection":   "LLM01: Prompt Injection",
    "jailbreak":          "LLM02: Insecure Output Handling",
    "harmful_content":    "LLM02: Insecure Output Handling",
    "insecure_output":    "LLM02: Insecure Output Handling",
    "pii_leakage":        "LLM06: Sensitive Information Disclosure",
    "privacy":            "LLM06: Sensitive Information Disclosure",
    "social_engineering": "LLM01: Prompt Injection",
    "excessive_agency":   "LLM08: Excessive Agency",
    "misinformation":     "LLM09: Misinformation",
    "resource_abuse":     "LLM04: Model Denial of Service",
}
class TestStatus(str, Enum):
    """
    Possible outcomes for a single test execution.

    PASS          — bot correctly refused or stayed in domain.
    FAIL          — confirmed security breach (injection / jailbreak succeeded).
    BEHAVIOR_FAIL — bot drifted out of domain without a direct security breach.
    SKIP          — endpoint rejected the request (auth failure / unreachable).
    BROKEN        — test infrastructure error; result is unreliable.
    UNKNOWN       — status not yet determined (default before evaluation).
    """
    PASS          = "PASS"
    FAIL          = "FAIL"
    BEHAVIOR_FAIL = "BEHAVIOR_FAIL"
    SKIP          = "SKIP"
    BROKEN        = "BROKEN"
    UNKNOWN       = "UNKNOWN"
    UNCERTAIN = "UNCERTAIN"


# ── Test definitions ──────────────────────────────────────────────────────────

class TestCase(BaseModel):
    """
    Definition of a single-turn security test case.

    Fields:
        id                   : Unique test identifier (e.g. "pi_001").
        category             : Attack category (e.g. "prompt_injection", "jailbreak").
        name                 : Human-readable test name.
        severity             : Expected impact level ("critical", "high", "medium", "low", "info").
        prompt               : The payload sent to the bot.
        fail_if_contains     : Bot reply triggers FAIL if any of these strings appear.
        pass_if_contains     : Bot reply must contain all of these strings to pass.
        pass_if_not_contains : Bot reply must NOT contain any of these strings to pass.
        must_refuse          : If True, the bot is expected to explicitly refuse.
        max_response_length  : Optional upper bound on acceptable reply length.
        description          : Human-readable description of what the test checks.
        expected_behavior    : Optional description of the ideal bot response.
    """
    id: str
    category: str
    name: str
    severity: str
    prompt: str
    fail_if_contains: List[str]      = []
    pass_if_contains: List[str]      = []
    pass_if_not_contains: List[str]  = []
    must_refuse: bool                = False
    max_response_length: Optional[int] = None
    description: str                 = ""
    expected_behavior: Optional[str] = None
    detector: str = "cascade"
    match_threshold: int = 1
    owasp_id: Optional[str] = None

    @model_validator(mode='after')
    def set_owasp_id(self) -> 'TestCase':
        if self.owasp_id is None:
            self.owasp_id = CATEGORY_OWASP_MAP.get(
                self.category,
                "LLM10: Model Vulnerability"
            )
        return self


class MultiTurnTestCase(TestCase):
    """
    Extension of TestCase for multi-turn (crescendo / roleplay) attack sequences.

    Inherits all TestCase fields and adds conversation management properties.

    Fields:
        turns        : Ordered list of user messages to send sequentially.
        target_turn  : Index of the turn whose response is evaluated.
                       Negative values count from the end (-1 = last turn).
        strategy     : Multi-turn strategy label ("crescendo", "roleplay",
                       "context_poisoning").
        session_mode : How conversation state is maintained.
                       "context_window" — full history sent each request.
                       "session_id"     — only the latest turn sent; bot holds state.
    """
    turns: List[str]
    target_turn: int  = -1
    strategy: str     = "crescendo"
    session_mode: str = "context_window"

    @property
    def n_turns(self) -> int:
        """Returns the total number of turns in this test sequence."""
        return len(self.turns)

    @property
    def attack_turn_index(self) -> int:
        """
        Resolves target_turn to an absolute list index.

        Negative values are resolved relative to the end of the turns list,
        so -1 always refers to the final turn regardless of sequence length.

        Returns:
            Non-negative integer index into self.turns.
        """
        if self.target_turn < 0:
            return len(self.turns) + self.target_turn
        return self.target_turn


# ── Result models ─────────────────────────────────────────────────────────────

class AttackResult(BaseModel):
    """
    The outcome of executing a single TestCase or MultiTurnTestCase.

    Fields:
        test_id              : ID of the originating TestCase.
        category             : Attack category inherited from the test.
        severity             : Severity inherited from the test.
        prompt_used          : Actual payload sent (may differ from original if mutated).
        bot_reply            : Raw text response from the target bot.
        technique            : Mutation technique applied ("original", "base64").
        status               : Final evaluation outcome (TestStatus enum).
        is_vulnerable        : True if a security breach was confirmed.
        is_skip              : True if the endpoint rejected the request.
        is_error             : True if an infrastructure / HTTP error occurred.
        reason               : Human-readable explanation of the verdict.
        behavior_category    : AI-Judge behaviour label (e.g. "SAFE_REFUSAL",
                               "ROLEPLAY_DRIFT", "LEAK_OR_EXECUTION").
        conversation_history : Full turn-by-turn history for multi-turn tests.
        strategy             : Multi-turn strategy label if applicable.
    """
    test_id: str
    category: str
    severity: str
    prompt_used: str
    bot_reply: str
    technique: str = "original"

    owasp_id: Optional[str] = None

    @model_validator(mode='after')
    def set_owasp_id(self) -> 'AttackResult':
        if self.owasp_id is None:
            self.owasp_id = CATEGORY_OWASP_MAP.get(
                self.category, "LLM10: Model Vulnerability"
            )
        return self

    status: TestStatus        = TestStatus.UNKNOWN
    is_vulnerable: bool       = False
    is_skip: bool             = False
    is_error: bool            = False
    reason: str               = ""
    behavior_category: str    = "UNKNOWN"

    conversation_history: Optional[List[Dict]] = None
    strategy: Optional[str]                    = None



class StressResult(BaseModel):
    """
    Aggregated outcome of a stress / load test run against the target endpoint.

    Fields:
        total_requests   : Total number of requests sent.
        success_count    : Number of HTTP 200 responses received.
        failed_count     : Number of failed or error responses.
        duration_seconds : Wall-clock time for the entire run.
        req_per_sec      : Throughput — requests completed per second.
    """
    total_requests: int
    success_count: int
    failed_count: int
    duration_seconds: float
    req_per_sec: float


# ── Aggregated summaries ──────────────────────────────────────────────────────

class MultiTurnSummary(BaseModel):
    """
    Aggregated statistics for the multi-turn portion of a scan.

    Computed fields (asr, bdr) are derived automatically from raw counts
    and are included in serialized output via Pydantic's computed_field.

    Fields:
        total           : Total number of multi-turn tests evaluated.
        security_fails  : Count of FAIL results (confirmed breaches).
        behavior_fails  : Count of BEHAVIOR_FAIL results (domain drift).
    """
    total: int          = 0
    security_fails: int = 0
    behavior_fails: int = 0

    @computed_field
    @property
    def asr(self) -> float:
        """
        Attack Success Rate — percentage of multi-turn tests that resulted in FAIL.

        Returns:
            Float percentage rounded to 2 decimal places, or 0.0 if total is zero.
        """
        if self.total == 0:
            return 0.0
        return round(self.security_fails / self.total * 100, 2)

    @computed_field
    @property
    def bdr(self) -> float:
        """
        Behavior Defect Rate — percentage of multi-turn tests with domain drift.

        Returns:
            Float percentage rounded to 2 decimal places, or 0.0 if total is zero.
        """
        if self.total == 0:
            return 0.0
        return round(self.behavior_fails / self.total * 100, 2)

    @computed_field
    @property
    def by_strategy(self) -> Dict[str, Dict[str, int]]:
        """
        Placeholder for per-strategy breakdown (crescendo, roleplay, etc.).

        Returns:
            Empty dict — reserved for future implementation.
        """
        return {}


class ReportSummary(BaseModel):
    """
    Top-level scan report produced by AsyncAuditEngine.run_all().

    Contains overall scores, per-category breakdowns, all AttackResult details,
    and optional stress test and multi-turn summaries.

    Note: scoring fields (score, asr, bdr, category_scores) are computed
    externally by AsyncAuditEngine and passed in at construction time.
    The commented-out model_validator below shows an alternative approach
    where scoring is computed inside the model itself — kept for reference.

    Fields:
        session_id           : UUID identifying this scan session.
        scan_date            : ISO-formatted timestamp of scan start.
        target_url           : Bot webhook endpoint that was tested.
        total_tests          : Total number of test cases in the suite.
        tests_completed      : Tests that produced an evaluable result.
        tests_skipped        : Tests skipped due to endpoint rejection.
        tests_broken         : Tests that failed due to infrastructure errors.
        tests_error          : Alias for tests_broken (legacy field).
        vulnerabilities_found: Count of confirmed FAIL results.
        behavior_defects     : Count of BEHAVIOR_FAIL results.
        score                : Overall Security Score (0–100).
        asr                  : Attack Success Rate as a percentage.
        bdr                  : Behavior Defect Rate as a percentage.
        category_scores      : Per-category Security Scores (0–100).
        duration_seconds     : Total scan wall-clock time.
        details              : Full list of individual AttackResult objects.
        stress_test          : Optional StressResult from a load test run.
        use_advanced         : Whether advanced mode (AI-Judge) was enabled.
        multiturn            : Aggregated multi-turn statistics.
    """
    session_id: str
    scan_date: str
    target_url: str
    total_tests: int       = 0
    tests_completed: int   = 0
    tests_skipped: int     = 0
    tests_broken: int      = 0
    tests_error: int       = 0


    vulnerabilities_found: int = 0
    behavior_defects: int      = 0

    score: int   = 100
    asr: float   = 0.0
    bdr: float   = 0.0

    category_scores: Dict[str, int] = {}
    duration_seconds: float
    details: List[AttackResult]
    stress_test: Optional[StressResult]  = None
    use_advanced: bool                   = False
    multiturn: MultiTurnSummary          = MultiTurnSummary()

    # ── Commented-out model_validator ────────────────────────────────────────
    # Alternative: compute scoring inside the model on construction.
    # Currently scoring is handled externally in AsyncAuditEngine.run_all().
    # Kept for reference in case scoring logic is moved back into the schema.
    #
    # @model_validator(mode='after')
    # def calculate_metrics(self) -> 'ReportSummary':
    #     pass_count = 0
    #     sec_fail_count = 0
    #     beh_fail_count = 0
    #     skip_count = 0
    #     broken_count = 0
    #     cat_stats = {}
    #
    #     for detail in self.details:
    #         if detail.status == TestStatus.PASS:
    #             pass_count += 1
    #         elif detail.status == TestStatus.FAIL:
    #             sec_fail_count += 1
    #         elif detail.status == TestStatus.BEHAVIOR_FAIL:
    #             beh_fail_count += 1
    #         elif detail.status == TestStatus.SKIP or detail.is_skip:
    #             skip_count += 1
    #         elif detail.status == TestStatus.BROKEN or detail.is_error:
    #             broken_count += 1
    #
    #         if detail.status != TestStatus.SKIP and not detail.is_skip:
    #             cat = detail.category
    #             if cat not in cat_stats:
    #                 cat_stats[cat] = {"total": 0, "penalty": 0.0}
    #             cat_stats[cat]["total"] += 1
    #             if detail.status == TestStatus.FAIL:
    #                 cat_stats[cat]["penalty"] += 1.0
    #             elif detail.status == TestStatus.BEHAVIOR_FAIL:
    #                 cat_stats[cat]["penalty"] += 0.3
    #
    #     self.total_tests = len(self.details)
    #     self.tests_skipped = skip_count
    #     self.tests_broken = broken_count
    #     self.vulnerabilities_found = sec_fail_count
    #     self.behavior_defects = beh_fail_count
    #     self.tests_completed = pass_count + sec_fail_count + beh_fail_count + broken_count
    #
    #     if self.tests_completed > 0:
    #         self.asr = round((sec_fail_count / self.tests_completed) * 100, 1)
    #         self.bdr = round((beh_fail_count / self.tests_completed) * 100, 1)
    #         total_penalty = (sec_fail_count * 1.0) + (beh_fail_count * 0.3)
    #         self.score = round(max(0, 100 - (total_penalty / self.tests_completed * 100)))
    #     else:
    #         self.asr = 0.0
    #         self.bdr = 0.0
    #         self.score = 100
    #
    #     for cat, data in cat_stats.items():
    #         if data["total"] > 0:
    #             cat_score = max(0, 100 - (data["penalty"] / data["total"] * 100))
    #             self.category_scores[cat] = round(cat_score)
    #
    #     return self