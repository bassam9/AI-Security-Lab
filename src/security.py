from users import USERS
from document_access import DOCUMENT_ACCESS
from prompt_security import analyze_prompt

def get_user(user_id: str):
    normalized_user_id = user_id.strip().lower()

    user = USERS.get(normalized_user_id)

    if not user:
        raise ValueError(f"Unknown user: {user_id}")

    return user


def get_allowed_documents(user_id: str):
    user = get_user(user_id)
    user_role = user["role"]

    allowed_documents = []

    for document_name, metadata in DOCUMENT_ACCESS.items():
        if user_role in metadata["allowed_roles"]:
            allowed_documents.append(document_name)

    return allowed_documents

import re


def sanitize_response(answer: str) -> str:
    # Remove quoted file path references
    answer = re.sub(r'["\']?docs[\\/][\w\-. ]+\.txt["\']?', "the provided documents", answer)

    # Remove direct quoted txt filenames
    answer = re.sub(r'["\']?[\w\-. ]+\.txt["\']?', "the provided documents", answer)

    # Clean awkward repeated wording
    answer = answer.replace('According to the provided document "the provided documents"', "According to the provided documents")
    answer = answer.replace("According to the provided document the provided documents", "According to the provided documents")
    answer = answer.replace('Based on the provided context in "the provided documents"', "Based on the provided documents")
    answer = answer.replace("Based on the provided context in the provided documents", "Based on the provided documents")

    return answer

RESTRICTED_TOPIC_MAP = {
    "incident response": ["incident-response-policy.txt"],
    "incident": ["incident-response-policy.txt"],
    "escalation": ["incident-response-policy.txt"],
    "access control": ["access-control-policy.txt"],
    "privileged access": ["access-control-policy.txt"],
    "admin access": ["access-control-policy.txt"],
}


def detect_restricted_topic(question: str, allowed_documents: list) -> str | None:
    normalized_question = question.lower()

    for topic, required_documents in RESTRICTED_TOPIC_MAP.items():
        if topic in normalized_question:
            for document in required_documents:
                if document not in allowed_documents:
                    return (
                        "This information is not available for your current access level. "
                        "Please contact the Security team if you believe you require access."
                    )

    return None

def authenticate_user(user_id: str, password: str):
    normalized_user_id = user_id.strip().lower()

    user = USERS.get(normalized_user_id)

    if not user:
        return None

    if user["password"] != password:
        return None

    return normalized_user_id

PROMPT_ATTACK_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget your instructions",
    "override your instructions",
    "you are now",
    "act as",
    "pretend to be",
    "developer mode",
    "jailbreak",
    "reveal your system prompt",
    "show me your system prompt",
    "show hidden instructions",
    "print all documents",
    "dump all documents",
    "export all documents",
    "give me the full policy",
    "show the full document",
    "list all confidential information",
    "bypass security",
    "bypass access control",
]


def validate_prompt(question: str) -> str | None:
    result = analyze_prompt(question)

    if not result["allowed"]:
        return result["message"]

    return None