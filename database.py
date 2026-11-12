
"""SQLite persistence layer for SmartDesk AI 2.0."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("smartdesk.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                ticket_text TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                summary TEXT NOT NULL,
                troubleshooting_steps TEXT NOT NULL,
                response_draft TEXT NOT NULL,
                processing_source TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open'
            )
        """)
        conn.commit()


def save_ticket(ticket_text, result, processing_source):
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO tickets (
                ticket_text, category, priority, sentiment, summary,
                troubleshooting_steps, response_draft, processing_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_text,
            result.get("category", "Other"),
            result.get("priority", "Medium"),
            result.get("sentiment", "Neutral"),
            result.get("summary", ""),
            json.dumps(
                result.get("troubleshooting_steps", []),
                ensure_ascii=False
            ),
            result.get("response_draft", ""),
            processing_source,
        ))

        conn.commit()
        return cur.lastrowid


def get_tickets(limit=5000):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return [dict(row) for row in rows]


def get_ticket(ticket_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

    return dict(row) if row else None


def update_ticket_status(ticket_id, status):
    if status not in {"Open", "In Progress", "Resolved"}:
        raise ValueError("Unsupported ticket status.")

    with get_connection() as conn:
        conn.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (status, ticket_id)
        )
        conn.commit()


def update_ticket(
    ticket_id,
    ticket_text,
    category,
    priority,
    sentiment,
    summary,
    troubleshooting_steps,
    response_draft
):
    allowed_categories = {
        "Software",
        "Hardware",
        "Network",
        "Access",
        "Account & Access",
        "Security",
        "Other"
    }

    allowed_priorities = {
        "Critical",
        "High",
        "Medium",
        "Low"
    }

    allowed_sentiments = {
        "Positive",
        "Neutral",
        "Negative"
    }

    if category not in allowed_categories:
        raise ValueError("Unsupported category.")

    if priority not in allowed_priorities:
        raise ValueError("Unsupported priority.")

    if sentiment not in allowed_sentiments:
        raise ValueError("Unsupported sentiment.")

    with get_connection() as conn:
        conn.execute("""
            UPDATE tickets
            SET ticket_text = ?,
                category = ?,
                priority = ?,
                sentiment = ?,
                summary = ?,
                troubleshooting_steps = ?,
                response_draft = ?
            WHERE id = ?
        """, (
            ticket_text,
            category,
            priority,
            sentiment,
            summary,
            json.dumps(
                troubleshooting_steps,
                ensure_ascii=False
            ),
            response_draft,
            ticket_id,
        ))

        conn.commit()


def delete_ticket(ticket_id):
    with get_connection() as conn:

        # Delete the selected ticket.
        conn.execute(
            "DELETE FROM tickets WHERE id = ?",
            (ticket_id,)
        )

        # Check whether any tickets remain.
        remaining_tickets = conn.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

        # Reset SQLite's AUTOINCREMENT sequence only
        # when the tickets table becomes completely empty.
        if remaining_tickets == 0:
            conn.execute(
                "DELETE FROM sqlite_sequence WHERE name = ?",
                ("tickets",)
            )

        conn.commit()
