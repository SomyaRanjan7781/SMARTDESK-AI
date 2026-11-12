
"""Local deterministic fallback. This is not generative AI."""

import re

KEYWORDS = {
    "Security": [
        "phishing", "hacked", "malware", "ransomware",
        "suspicious login", "breach", "virus"
    ],
    "Network": [
        "wifi", "wi-fi", "internet", "vpn",
        "network", "connection", "dns"
    ],
    "Hardware": [
        "laptop", "keyboard", "mouse", "monitor",
        "printer", "battery", "screen"
    ],
    "Account & Access": [
        "password", "login", "log in", "locked out",
        "access", "mfa", "two-factor"
    ],
    "Software": [
        "application", "software", "install", "crash",
        "error", "update", "outlook", "browser"
    ],
}


def analyze_with_rules(ticket_text: str) -> dict:

    text = ticket_text.lower()

    # 1. Category Classification
    category = "Other"
    best_score = 0

    for candidate, words in KEYWORDS.items():
        score = sum(1 for word in words if word in text)

        if score > best_score:
            category = candidate
            best_score = score

    # 2. Priority Classification
    critical_terms = [
        "ransomware", "data breach", "company-wide outage",
        "entire company", "all users", "hacked"
    ]

    high_terms = [
        "cannot work", "can't work", "unable to work",
        "locked out", "vpn", "production down"
    ]

    low_terms = [
        "how do i", "how to", "request",
        "suggestion", "minor"
    ]

    if any(term in text for term in critical_terms):
        priority = "Critical"

    elif any(term in text for term in high_terms):
        priority = "High"

    elif any(term in text for term in low_terms):
        priority = "Low"

    else:
        priority = "Medium"

    # 3. Sentiment Detection
    negative_words = [
        "angry", "frustrated", "urgent",
        "cannot", "can't", "not working", "broken"
    ]

    sentiment = (
        "Negative"
        if any(word in text for word in negative_words)
        else "Neutral"
    )

    # 4. Issue Summary
    clean = re.sub(r"\s+", " ", ticket_text).strip()

    summary = clean[:220] + (
        "..." if len(clean) > 220 else ""
    )

    # 5. Troubleshooting Suggestions
    steps_by_category = {

        "Security": [
            "Do not click suspicious links or open unexpected attachments.",
            "Do not share passwords or verification codes.",
            "Escalate immediately to the IT/security team using the approved incident process."
        ],

        "Network": [
            "Check whether other trusted websites or internal services are reachable.",
            "Reconnect to the approved network or VPN and note any error message.",
            "If multiple users are affected, escalate to the network support team."
        ],

        "Hardware": [
            "Check power, cable connections, and visible device indicators.",
            "Restart the device only if it is safe and no data is being transferred.",
            "Record the device model and any error indicators for IT support."
        ],

        "Account & Access": [
            "Check the username and approved sign-in page.",
            "Use the organisation's official password-reset or account-recovery process.",
            "Never share passwords or one-time verification codes with support."
        ],

        "Software": [
            "Record the application name, version, and exact error message.",
            "Close and reopen the application if doing so will not risk unsaved work.",
            "Check whether an approved update or known service issue is available."
        ],

        "Other": [
            "Collect the exact steps that led to the issue.",
            "Record any error message and when the problem began.",
            "Route the ticket to the appropriate support team for review."
        ]
    }

    # 6. Professional Response Generation
    response_draft = (
        "Hello,\n\n"
        "Thank you for reporting this issue. "
        f"We have recorded your request under {category} "
        f"with {priority} priority.\n\n"
        "Please try the suggested troubleshooting steps "
        "and share any exact error message with the IT support team.\n\n"
        "A support representative should review the ticket "
        "and advise on the next steps.\n\n"
        "Regards,\n"
        "IT Support"
    )

    # 7. Return Structured Result
    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "summary": summary,
        "troubleshooting_steps": steps_by_category[category],
        "response_draft": response_draft
    }
