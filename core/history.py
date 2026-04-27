# core/history.py
"""
Persistent scan history management for regression tracking and CI/CD integration.

Scan results are stored as newline-delimited JSON (JSONL) so that entries can be
appended without loading the entire file. Provides helpers for:
  - Appending a new scan entry       : save_to_history()
  - Reading the N most recent entries: load_history()
  - Fetching the previous scan entry : get_previous_scan()
  - Computing score / ASR deltas     : compute_delta()
  - Determining CI/CD exit codes     : get_ci_exit_code()
"""

# =============================================================================
# Default path for the JSONL history file
# =============================================================================
HISTORY_FILE = "reports/history.jsonl"

# =============================================================================
# Fields persisted per scan entry in the history log
# =============================================================================
HISTORY_ENTRY_FIELDS = [
    "timestamp",
    "session_id",
    "target_url",
    "score",
    "asr",
    "vulnerabilities_found",
    "tests_completed",
    "total_tests",
    "tests_skipped",
    "use_advanced",
    "duration_seconds",
    "category_scores",
]

# =============================================================================
# Built-in
# =============================================================================
import json
import os
from datetime import datetime
from typing import Optional

# =============================================================================
# Third-party
# (none)
# =============================================================================

# =============================================================================
# Local
# =============================================================================
from core.schemas import ReportSummary


def save_to_history(
    report: ReportSummary,
    history_path: str = HISTORY_FILE,
) -> None:
    """
    Appends a single scan result as a JSON line to the history log.

    Creates the parent directory if it does not exist. Each entry is a
    flat dict containing the fields listed in HISTORY_ENTRY_FIELDS plus
    an ISO-format timestamp generated at call time.

    Args:
        report:       Completed ReportSummary to persist.
        history_path: Path to the JSONL history file.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    entry = {
        "timestamp":              datetime.now().isoformat(),
        "session_id":             report.session_id,
        "target_url":             report.target_url,
        "score":                  report.score,
        "asr":                    report.asr,
        "vulnerabilities_found":  report.vulnerabilities_found,
        "tests_completed":        report.tests_completed,
        "total_tests":            report.total_tests,
        "tests_skipped":          report.tests_skipped,
        "use_advanced":           report.use_advanced,
        "duration_seconds":       report.duration_seconds,
        "category_scores":        report.category_scores,
    }

    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_history(
    history_path: str = HISTORY_FILE,
    limit: int = 10,
) -> list[dict]:
    """
    Loads the most recent N scan entries from the JSONL history file.

    Silently skips malformed lines so that a single corrupt entry does
    not break the entire history read.

    Args:
        history_path: Path to the JSONL history file.
        limit:        Maximum number of entries to return (most recent first).

    Returns:
        List of scan entry dicts ordered oldest → newest, capped at `limit`.
        Returns an empty list if the file does not exist.
    """
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
                    # Skip corrupt lines without aborting the read
                    continue

    return entries[-limit:]


def get_previous_scan(
    history_path: str = HISTORY_FILE,
    target_url: Optional[str] = None,
) -> Optional[dict]:
    """
    Returns the most recent *previous* scan entry from history.

    When target_url is provided, only entries matching that URL are considered,
    making regression comparison reliable across multi-target setups.

    The function intentionally skips the last entry in the filtered list
    because the caller is expected to have just appended the current scan —
    so the second-to-last entry represents the true previous run.

    Args:
        history_path: Path to the JSONL history file.
        target_url:   Optional bot endpoint URL to filter history by.

    Returns:
        A scan entry dict for the previous run, or None if fewer than two
        matching entries exist.
    """
    history = load_history(history_path, limit=50)

    if not history:
        return None

    if target_url:
        # Narrow history to entries for the same target endpoint
        filtered = [e for e in history if e.get("target_url") == target_url]
        # Need at least 2 entries: [-1] is current, [-2] is previous
        if len(filtered) >= 2:
            return filtered[-2]
        return None

    # Without a URL filter, compare against the second-to-last overall entry
    if len(history) >= 2:
        return history[-2]
    return None


def compute_delta(
    current: ReportSummary,
    previous: Optional[dict],
) -> Optional[dict]:
    """
    Computes the score, ASR, and vulnerability count deltas between two scans.

    A positive score_delta means security improved.
    A positive asr_delta means the attack success rate worsened.

    Args:
        current:  The just-completed ReportSummary.
        previous: A history entry dict from get_previous_scan(), or None.

    Returns:
        Dict with delta values and previous-scan metadata, or None if there
        is no previous scan to compare against.
    """
    if previous is None:
        return None

    score_delta = current.score - previous["score"]
    asr_delta   = round(current.asr - previous["asr"], 2)
    vuln_delta  = current.vulnerabilities_found - previous["vulnerabilities_found"]

    return {
        "previous_score":      previous["score"],
        "previous_asr":        previous["asr"],
        "previous_vulns":      previous["vulnerabilities_found"],
        "previous_timestamp":  previous["timestamp"],
        "previous_session_id": previous["session_id"],
        "score_delta":         score_delta,
        "asr_delta":           asr_delta,
        "vuln_delta":          vuln_delta,
    }


def get_ci_exit_code(
    current: ReportSummary,
    previous: Optional[dict],
    asr_threshold: float = 0.0,
) -> int:
    """
    Determines the CI/CD pipeline exit code based on ASR regression.

    Fails the pipeline (exit 1) in two cases:
      1. Current ASR exceeds the configured absolute threshold.
      2. Current ASR is higher than the previous scan's ASR (regression).

    Args:
        current:       The just-completed ReportSummary.
        previous:      Previous scan entry dict, or None if no history exists.
        asr_threshold: Absolute ASR value above which the pipeline should fail.
                       Defaults to 0.0 (any attack success fails the build).

    Returns:
        0 — no regression detected, pipeline passes.
        1 — regression detected or threshold exceeded, pipeline fails.
    """
    if current.asr > asr_threshold:
        return 1

    # Regression check: ASR increased compared to the previous run
    if previous and current.asr > previous.get("asr", 0):
        return 1

    return 0