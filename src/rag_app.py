from getpass import getpass
from pathlib import Path

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from config import configure_ai_settings
from prompts import security_qa_template
from logger import setup_audit_log, write_audit_log
from security import (
    authenticate_user,
    get_user,
    get_allowed_documents,
    detect_restricted_topic,
    sanitize_response,
    validate_prompt,
)


def build_query_engine(user_id: str):
    """Build a query engine using only documents the user is authorized to access."""

    configure_ai_settings()

    allowed_documents = get_allowed_documents(user_id)

    input_files = [
        str(Path("docs") / file_name)
        for file_name in allowed_documents
    ]

    documents = SimpleDirectoryReader(input_files=input_files).load_data()

    if not documents:
        raise ValueError("No authorized documents found for this user.")

    for document in documents:
        file_name = Path(document.metadata.get("file_path", "")).name
        document.metadata["file_name"] = file_name
        document.metadata["authorized_user"] = user_id

    index = VectorStoreIndex.from_documents(documents)

    return index.as_query_engine(
        similarity_top_k=3,
        response_mode="compact",
        text_qa_template=security_qa_template,
    )


def login():
    """Authenticate the user."""

    print("========== Secure RAG AI Assistant ==========\n")

    username = input("Username: ").strip().lower()
    password = getpass("Password: ").strip()

    authenticated_user = authenticate_user(username, password)

    if authenticated_user is None:
        print("\nAuthentication failed.")
        return None

    user = get_user(authenticated_user)

    print(f"\nWelcome {user['display_name']}!")
    print(f"Role: {user['role']}\n")

    return authenticated_user


def main():
    user_id = login()

    if user_id is None:
        return

    setup_audit_log()

    allowed_documents = get_allowed_documents(user_id)
    query_engine = build_query_engine(user_id)

    print("Secure RAG Assistant is running.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please type a question.\n")
            continue

        prompt_guardrail_message = validate_prompt(question)

        if prompt_guardrail_message:
            print("\nAnswer:")
            print(prompt_guardrail_message)
            print()
            write_audit_log(question, prompt_guardrail_message)
            continue

        access_denied = detect_restricted_topic(
            question,
            allowed_documents,
        )

        if access_denied:
            print("\nAnswer:")
            print(access_denied)
            print()
            write_audit_log(question, access_denied)
            continue

        response = query_engine.query(question)
        answer = sanitize_response(str(response))

        print("\nAnswer:")
        print(answer)
        print()

        write_audit_log(question, answer)


if __name__ == "__main__":
    main()