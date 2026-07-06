from datetime import datetime
import os
import csv


LOG_FILE = "logs/rag_audit_log.csv"


def setup_audit_log():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "user_question",
                "assistant_answer"
            ])


def write_audit_log(question: str, answer: str):
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            question,
            answer
        ])