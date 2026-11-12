# SmartDesk AI 🎫

**AI-Assisted IT Service Desk & Ticket Triage System**

SmartDesk AI is a Streamlit-based IT helpdesk application that turns unstructured support requests into structured, actionable tickets. It combines Google Gemini-powered analysis with deterministic local fallback rules, SQLite ticket storage, ticket lifecycle management, and operational analytics.

> **Live application:** https://smartdesk-ai-bcsmqqqge6qsyqdx9xqrgx.streamlit.app/  
> **Source code:** https://github.com/SomyaRanjan7781/SMARTDESK-AI

---

## Overview

IT support teams receive requests about hardware, software, network connectivity, account access, and security. Before support staff can act, they need to understand the issue, assess urgency, organise the request, and prepare a response.

SmartDesk AI assists with this initial triage process. A support request is analysed and stored as a ticket with a category, priority, sentiment, summary, troubleshooting recommendations, and a draft response. Support staff can then search, review, edit, update, export, and monitor tickets.

SmartDesk AI is an **AI-assisted workflow prototype**, not a replacement for a full enterprise IT service management platform.

## Key Features

### AI-assisted ticket triage
- Uses the Google Gemini API to analyse free-text IT support requests.
- Produces a structured result containing:
  - **Category:** Software, Hardware, Network, Account & Access, Security, or Other.
  - **Priority:** Critical, High, Medium, or Low.
  - **Sentiment:** Positive, Neutral, or Negative.
  - **Issue summary**
  - **Suggested troubleshooting steps**
  - **Professional draft response**

### Multiple processing modes
| Mode | Behaviour |
|---|---|
| **Auto (recommended)** | Tries Gemini first and uses local fallback rules if the Gemini request fails. |
| **Live AI** | Attempts Gemini analysis; if the request fails, the application uses local fallback rules and surfaces the technical error. |
| **Fallback rules** | Runs deterministic keyword-based classification and recommendations locally, without calling Gemini. |
| **Demo** | Uses predefined sample tickets from `demo_data.py`. |

### Ticket management
- Stores tickets in SQLite.
- Displays ticket details and processing source.
- Searches tickets by ID, issue description, or summary.
- Filters by category, priority, status, and creation period.
- Updates ticket information and status.
- Deletes tickets.
- Resets the next ticket ID to **1 when the tickets table becomes empty**.

### Dashboard and analytics
- Overview of total, open, in-progress, critical, and resolved tickets.
- Recent ticket activity.
- Ticket status, priority, and category charts.
- Analytics for ticket volume, average priority score, resolved tickets, AI-processed tickets, and processing source.
- Date filters for all time, today, and the last 7, 30, or 90 days.

### Export and usability
- Download an individual ticket record as CSV.
- Export filtered ticket records as CSV.
- Displays a refresh/help reminder in the application UI.

## Application Workflow

1. An employee or support user enters an issue description.
2. The selected processing mode analyses the description.
3. Gemini returns structured analysis, or local rules provide deterministic fallback output.
4. The result is saved as a ticket in SQLite.
5. A support representative reviews the suggested troubleshooting and draft response.
6. The ticket can be searched, edited, assigned a status, deleted, and included in dashboard analytics.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Web application | Streamlit |
| Generative AI | Google Gemini API |
| Gemini SDK | `google-genai` |
| Local fallback analysis | Python keyword and rule-based logic |
| Database | SQLite |
| Data handling | Pandas |
| Analytics visualisations | Streamlit charts |

## Project Structure

```text
SMARTDESK-AI/
├── app.py             # Streamlit UI, navigation, dashboard and workflows
├── ai_service.py      # Gemini API integration and structured response validation
├── database.py        # SQLite connection and ticket CRUD operations
├── rules.py           # Deterministic local fallback analysis
├── demo_data.py       # Predefined sample tickets for Demo mode
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SomyaRanjan7781/SMARTDESK-AI.git
cd SMARTDESK-AI
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The current `requirements.txt` includes Streamlit, Google Gen AI SDK, and Pandas.

### 4. Configure the Gemini API key

Live AI and Auto modes require a Gemini API key. The application reads the key from Streamlit secrets first, then from the `GEMINI_API_KEY` environment variable.

**Local Streamlit secrets**

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

**Alternatively, set an environment variable:**

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

macOS / Linux:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Do not hard-code API keys in Python files or commit them to GitHub. For Streamlit Community Cloud, add `GEMINI_API_KEY` in the app's **Settings → Secrets**.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501.

## Database

The application initialises a SQLite database named `smartdesk.db` alongside `database.py` when it starts.

The database stores:
- Original ticket description
- Category, priority, and sentiment
- Issue summary
- Troubleshooting steps
- Draft response
- Processing source
- Ticket creation time and status

The database is local to the running environment. On a hosted platform, persistence across restarts or redeployments depends on that platform's storage configuration. For a multi-user production deployment, use a persistent shared database and add authentication and access controls.

## Deployment

The application is deployed on Streamlit Community Cloud:

**https://smartdesk-ai-bcsmqqqge6qsyqdx9xqrgx.streamlit.app/**

To deploy your own instance:
1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select `app.py` as the main application file.
3. Configure `GEMINI_API_KEY` under the app's Secrets settings.
4. Deploy and verify the application.

## Privacy, Safety, and Human Review

- Use fictional or anonymised ticket descriptions when demonstrating the project.
- Never enter passwords, one-time codes, API keys, authentication tokens, or confidential company information.
- Keep API credentials in environment variables or Streamlit secrets.
- AI-generated classifications and recommendations are suggestions, not verified diagnoses.
- A human support representative should review troubleshooting steps and draft responses before acting on them.
- The application does not send replies or execute troubleshooting actions automatically.

## Current Limitations

- Local fallback analysis is deterministic and keyword-based; it is not generative AI and may not understand every wording or context.
- Gemini availability, latency, and usage depend on the selected model and Google API service limits. Temporary server errors can result in fallback processing.
- The current prototype does not include employee authentication, role-based access, SLA enforcement, automatic escalation, email notifications, or integrations with external ITSM platforms.
- SQLite is suitable for this prototype; a production multi-user service would require persistent shared storage and appropriate access controls.

## Future Enhancements

- Employee and support-agent authentication with role-based permissions.
- SLA monitoring and automatic escalation rules.
- Email or collaboration-platform notifications.
- Integration with platforms such as Jira Service Management or ServiceNow.
- Persistent cloud database for multi-user deployment.
- More detailed operational reporting and service-level metrics.

## Author

**Somya Ranjan**

---

*SmartDesk AI — AI-assisted IT service desk ticket triage and management.*
