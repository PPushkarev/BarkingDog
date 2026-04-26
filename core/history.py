import os
import json
from datetime import datetime
from typing import Optional
from core.schemas import ReportSummary


HISTORY_FILE = "reports/history.jsonl"


def save_to_history(report: ReportSummary, history_path: str = HISTORY_FILE) -> None:
    """Append a scan result to the history log."""
    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": report.session_id,
        "target_url": report.target_url,
        "score": report.score,
        "asr": report.asr,
        "vulnerabilities_found": report.vulnerabilities_found,
        "tests_completed": report.tests_completed,
        "total_tests": report.total_tests,
        "tests_skipped": report.tests_skipped,
        "use_advanced": report.use_advanced,
        "duration_seconds": report.duration_seconds,
        "category_scores": report.category_scores,
    }

    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_history(history_path: str = HISTORY_FILE, limit: int = 10) -> list[dict]:
    """Load last N scan entries from history."""
    if not os.path.exists(history_path):
        return []

    entries = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # Return last N entries
    return entries[-limit:]


def get_previous_scan(history_path: str = HISTORY_FILE, target_url: Optional[str] = None) -> Optional[dict]:
    """Get the most recent previous scan (optionally filtered by target URL)."""
    history = load_history(history_path, limit=50)

    if not history:
        return None

    if target_url:
        # Filter by same target, return second-to-last (last is current)
        filtered = [e for e in history if e.get("target_url") == target_url]
        # If we have at least 2 entries for this target, return the previous one
        if len(filtered) >= 2:
            return filtered[-2]
        return None

    # Without filter: return second-to-last overall
    if len(history) >= 2:
        return history[-2]
    return None


def compute_delta(current: ReportSummary, previous: Optional[dict]) -> Optional[dict]:
    """Compute score/ASR delta between current and previous scan."""
    if previous is None:
        return None

    score_delta = current.score - previous["score"]
    asr_delta = round(current.asr - previous["asr"], 2)
    vuln_delta = current.vulnerabilities_found - previous["vulnerabilities_found"]

    return {
        "previous_score": previous["score"],
        "previous_asr": previous["asr"],
        "previous_vulns": previous["vulnerabilities_found"],
        "previous_timestamp": previous["timestamp"],
        "previous_session_id": previous["session_id"],
        "score_delta": score_delta,
        "asr_delta": asr_delta,
        "vuln_delta": vuln_delta,
    }


def get_ci_exit_code(current: ReportSummary, previous: Optional[dict], asr_threshold: float = 0.0) -> int:
    """
    Returns exit code for CI/CD:
      0 = OK (ASR didn't increase)
      1 = REGRESSION (ASR increased vs previous scan OR exceeds threshold)
    """
    if current.asr > asr_threshold:
        return 1
    if previous and current.asr > previous.get("asr", 0):
        return 1
    return 0