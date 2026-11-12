
DEMO_TICKETS = {
    "VPN access issue": {
        "ticket": (
            "I cannot connect to the company VPN since this morning. "
            "I have restarted my laptop but it still fails with a "
            "connection timeout. I need access to internal tools "
            "to complete my work."
        ),
        "result": {
            "category": "Network",
            "priority": "High",
            "sentiment": "Negative",
            "summary": (
                "The user cannot connect to the company VPN and "
                "receives a connection timeout, blocking access "
                "to internal tools."
            ),
            "troubleshooting_steps": [
                "Check whether the internet connection works outside the VPN.",
                "Reconnect using the organisation's approved VPN client and capture the exact error.",
                "If the issue persists, escalate to network support and check whether other users are affected."
            ],
            "response_draft": (
                "Hello,\n\n"
                "Thank you for reporting the VPN issue. "
                "We understand that this is affecting your access to internal tools.\n\n"
                "Please confirm whether regular internet access is working "
                "and share the exact VPN error message.\n\n"
                "We will route this to network support for investigation.\n\n"
                "Regards,\n"
                "IT Support"
            )
        }
    },

    "Suspicious email": {
        "ticket": (
            "I received an email asking me to verify my account "
            "through an unfamiliar link. The sender address looks "
            "unusual and I am worried it may be phishing."
        ),
        "result": {
            "category": "Security",
            "priority": "Critical",
            "sentiment": "Negative",
            "summary": (
                "The user received a suspicious account-verification "
                "email that may be a phishing attempt."
            ),
            "troubleshooting_steps": [
                "Do not click the link or open attachments.",
                "Do not reply or provide credentials or verification codes.",
                "Report the email to the organisation's security team using the approved process."
            ],
            "response_draft": (
                "Hello,\n\n"
                "Thank you for reporting this suspicious email.\n\n"
                "Please do not click the link, open attachments, "
                "or provide any credentials.\n\n"
                "Kindly report or forward it using your organisation's "
                "approved phishing-reporting process.\n\n"
                "Our security team should review it promptly.\n\n"
                "Regards,\n"
                "IT Security"
            )
        }
    },

    "Printer not working": {
        "ticket": (
            "The printer near the meeting room is not printing. "
            "The display is on, but jobs remain in the queue."
        ),
        "result": {
            "category": "Hardware",
            "priority": "Medium",
            "sentiment": "Neutral",
            "summary": (
                "The meeting-room printer is powered on, but print "
                "jobs remain queued and are not completing."
            ),
            "troubleshooting_steps": [
                "Check the printer display for paper, toner, or connectivity warnings.",
                "Confirm the selected printer and queue on the computer.",
                "If the queue remains stuck, contact IT support with the printer location and any displayed error."
            ],
            "response_draft": (
                "Hello,\n\n"
                "Thank you for reporting the printer issue.\n\n"
                "Please check the printer display for any warning "
                "and confirm that the correct printer is selected.\n\n"
                "We will review the queue and arrange further support "
                "if required.\n\n"
                "Regards,\n"
                "IT Support"
            )
        }
    }
}
