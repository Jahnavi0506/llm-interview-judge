PROMPT_VERSIONS = {
    "question_prompt": {
        "version": "1.2",
        "description": "Added previous_questions exclusion to prevent repetition",
        "changelog": [
            "v1.0 — Initial prompt with domain, difficulty, topic",
            "v1.1 — Added difficulty guidelines section",
            "v1.2 — Added previous_questions exclusion block"
        ]
    },
    "evaluation_prompt": {
        "version": "1.2",
        "description": "Improved concept coverage rules to reduce false negatives",
        "changelog": [
            "v1.0 — Basic rubric-based evaluation",
            "v1.1 — Added concept coverage rules",
            "v1.2 — Added strict missing concept detection rules"
        ]
    },
    "report_prompt": {
        "version": "1.0",
        "description": "Overall interview report generation",
        "changelog": [
            "v1.0 — Initial overall report with recommendation"
        ]
    }
}


def get_prompt_version(prompt_name: str) -> str:
    return PROMPT_VERSIONS.get(prompt_name, {}).get("version", "unknown")


def get_all_versions() -> dict:
    return PROMPT_VERSIONS


def get_version_summary() -> str:
    lines = []
    for name, info in PROMPT_VERSIONS.items():
        lines.append(f"{name} v{info['version']}: {info['description']}")
    return "\n".join(lines)