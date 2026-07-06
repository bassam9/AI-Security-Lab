PROMPT_SECURITY_RULES = [
    {
        "category": "Prompt Injection",
        "severity": "High",
        "patterns": [
            "ignore previous instructions",
            "ignore all previous instructions",
            "disregard previous instructions",
            "forget your instructions",
            "override your instructions",
        ],
    },
    {
        "category": "Role Override",
        "severity": "High",
        "patterns": [
            "you are now",
            "act as",
            "pretend to be",
            "developer mode",
        ],
    },
    {
        "category": "System Prompt Disclosure",
        "severity": "High",
        "patterns": [
            "reveal your system prompt",
            "show me your system prompt",
            "show hidden instructions",
            "what are your instructions",
        ],
    },
    {
        "category": "Bulk Data Extraction",
        "severity": "Medium",
        "patterns": [
            "print all documents",
            "dump all documents",
            "export all documents",
            "show the full document",
            "give me the full policy",
        ],
    },
    {
        "category": "Security Bypass",
        "severity": "High",
        "patterns": [
            "bypass security",
            "bypass access control",
            "disable guardrails",
            "remove restrictions",
        ],
    },
]


def analyze_prompt(question: str):
    normalized_question = question.lower()

    for rule in PROMPT_SECURITY_RULES:
        for pattern in rule["patterns"]:
            if pattern in normalized_question:
                return {
                    "allowed": False,
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "matched_pattern": pattern,
                    "message": (
                        "Your request appears to conflict with the assistant security policy. "
                        "Please rephrase your question as a normal policy-related request."
                    ),
                }

    return {
        "allowed": True,
        "category": "Benign",
        "severity": "None",
        "matched_pattern": None,
        "message": None,
    }