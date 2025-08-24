import os
import re
from dotenv import load_dotenv

load_dotenv()


def summarize_logs(text: str) -> str:
    top = sorted(
        (
            (m.group(0), len(m.group(0)))
            for m in re.finditer(r"(ERROR|CRIT|ALARM).+", text)
        ),
        key=lambda x: -x[1],
    )
    if not os.getenv("OPENAI_API_KEY"):
        return f"Top incidents (heuristic): {min(len(top),5)} lines flagged."

    return "LLM summary not implemented in this snippet."


def extract_incidents(log_text: str) -> dict:
    """Extract incident patterns from syslog text"""
    patterns = {
        "critical_errors": re.findall(r"CRIT.*", log_text),
        "errors": re.findall(r"ERROR.*", log_text),
        "alarms": re.findall(r"ALARM.*", log_text),
        "warnings": re.findall(r"WARN.*", log_text),
    }

    return {
        "summary": summarize_logs(log_text),
        "incident_counts": {k: len(v) for k, v in patterns.items()},
        "top_incidents": patterns,
    }
