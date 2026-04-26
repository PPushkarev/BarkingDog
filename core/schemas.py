from pydantic import BaseModel, computed_field, model_validator
from typing import List, Optional, Dict
from enum import Enum


class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BEHAVIOR_FAIL = "BEHAVIOR_FAIL"
    SKIP = "SKIP"
    BROKEN = "BROKEN"
    UNKNOWN = "UNKNOWN"


class TestCase(BaseModel):
    id: str
    category: str
    name: str
    severity: str
    prompt: str
    fail_if_contains: List[str] = []
    pass_if_contains: List[str] = []
    pass_if_not_contains: List[str] = []
    must_refuse: bool = False
    max_response_length: Optional[int] = None
    description: str = ""
    expected_behavior: Optional[str] = None


class MultiTurnTestCase(TestCase):
    turns: List[str]
    target_turn: int = -1
    strategy: str = "crescendo"
    session_mode: str = "context_window"

    @property
    def n_turns(self) -> int:
        return len(self.turns)

    @property
    def attack_turn_index(self) -> int:
        if self.target_turn < 0:
            return len(self.turns) + self.target_turn
        return self.target_turn


# 1. Сначала объявляем AttackResult
class AttackResult(BaseModel):
    test_id: str
    category: str
    severity: str
    prompt_used: str
    bot_reply: str
    technique: str = "original"

    status: TestStatus = TestStatus.UNKNOWN
    is_vulnerable: bool = False
    is_skip: bool = False
    is_error: bool = False
    reason: str = ""
    behavior_category: str = "UNKNOWN"

    conversation_history: Optional[List[Dict]] = None
    strategy: Optional[str] = None


class StressResult(BaseModel):
    total_requests: int
    success_count: int
    failed_count: int
    duration_seconds: float
    req_per_sec: float


class MultiTurnSummary(BaseModel):
    total: int = 0
    security_fails: int = 0
    behavior_fails: int = 0

    @computed_field
    @property
    def asr(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.security_fails / self.total * 100, 2)

    @computed_field
    @property
    def bdr(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.behavior_fails / self.total * 100, 2)

    @computed_field
    @property
    def by_strategy(self) -> Dict[str, Dict[str, int]]:
        return {}


# 2. И только потом ReportSummary, который использует AttackResult
class ReportSummary(BaseModel):
    session_id: str
    scan_date: str
    target_url: str
    total_tests: int = 0
    tests_completed: int = 0
    tests_skipped: int = 0
    tests_broken: int = 0
    tests_error: int = 0

    vulnerabilities_found: int = 0
    behavior_defects: int = 0

    score: int = 100
    asr: float = 0.0
    bdr: float = 0.0

    category_scores: Dict[str, int] = {}
    duration_seconds: float
    details: List[AttackResult]
    stress_test: Optional[StressResult] = None
    use_advanced: bool = False
    multiturn: MultiTurnSummary = MultiTurnSummary()

    # @model_validator(mode='after')
    # def calculate_metrics(self) -> 'ReportSummary':
    #     pass_count = 0
    #     sec_fail_count = 0
    #     beh_fail_count = 0
    #     skip_count = 0
    #     broken_count = 0
    #
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
    #
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
    #
    #     self.tests_completed = pass_count + sec_fail_count + beh_fail_count + broken_count
    #
    #     if self.tests_completed > 0:
    #         self.asr = round((sec_fail_count / self.tests_completed) * 100, 1)
    #         self.bdr = round((beh_fail_count / self.tests_completed) * 100, 1)
    #
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