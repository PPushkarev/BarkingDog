# core/loader.py
import os
import yaml
from pathlib import Path


def load_all_checks(checks_dir: str) -> list[dict]:
    """
    Scans the directory for YAML files and returns a flat list of all test cases as dictionaries.
    It does not enforce any strict schema, allowing the Orchestrator to parse needed fields dynamically.
    """
    target_dir = Path(checks_dir)
    if not target_dir.exists() or not target_dir.is_dir():
        print(f"[!] Error: Directory not found - {target_dir}")
        return []

    all_cases = []

    # Iterate over all .yaml files in the directory
    for yaml_file in target_dir.glob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, list):
                    all_cases.extend(data)
        except Exception as e:
            print(f"[!] Error parsing {yaml_file.name}: {e}")

    print(f"[*] Loaded {len(all_cases)} raw cases from {checks_dir}")
    return all_cases