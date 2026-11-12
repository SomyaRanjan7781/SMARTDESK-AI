# SmartDesk AI 🎫

**AI-powered IT Helpdesk Automation and Ticket Management System**

SmartDesk AI is a Streamlit-based application that helps support teams
analyse IT support tickets, estimate urgency, suggest safe first
troubleshooting steps, and prepare professional response drafts.

## Features

-   **AI-assisted ticket triage:** Uses Google Gemini to analyse ticket
    descriptions and generate structured recommendations.
-   **Automatic fallback:** In Auto mode, the app attempts Gemini
    analysis and falls back to local keyword-based rules if the AI
    service is unavailable.
-   **Rule-based processing:** Analyse tickets locally using predefined
    keyword and classification rules.
-   **Demo mode:** Explore the application with preloaded sample
    tickets.
-   **Ticket management:** View ticket details and update status (Open,
    In Progress, Resolved).
-   **Search and filters:** Find tickets by ID, issue description, or
    summary, and filter by category, priority, and status.
-   **Dashboard and analytics:** View ticket counts, recent activity,
    and charts for categories, priorities, and processing sources.
-   **CSV export:** Download ticket analysis or matching ticket records.

## Tech stack

-   Python
-   Streamlit
-   SQLite
-   Pandas
-   Google Gemini API (`google-genai`)
-   Streamlit charts (and any additional charting libraries used in your
    implementation)

## Project structure

``` text
SMARTDESK-AI/
├── app.py                 # Streamlit application and UI
├── ai_service.py          # Gemini-powered ticket analysis
├── database.py            # SQLite database operations
├── rules.py               # Local keyword-based fallback analysis
├── demo_data.py           # Preloaded demonstration tickets
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

> Keep filenames consistent with your actual repository. Add or remove
> entries above if your local project differs.

## Getting started

### 1. Clone the repository

``` bash
git clone https://github.com/SomyaRanjan7781/SMARTDESK-AI.git
cd SMARTDESK-AI
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

If `requirements.txt` is not present yet, create it from the packages
used by the project, then run the command above.

### 4. Configure Gemini (optional)

Live AI analysis requires a valid Google Gemini API key. Set the
environment variable expected by your `ai_service.py` implementation.
For example, if your code uses the Google Gen AI SDK's `GOOGLE_API_KEY`
variable:

**Windows PowerShell:**

``` powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

**macOS / Linux:**

``` bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Do not paste API keys into source code or commit them to GitHub. If
`ai_service.py` uses a different environment-variable name, use that
exact name instead.

### 5. Run the application

``` bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) that
you can open in your browser.

## Processing modes

  -----------------------------------------------------------------------
  Mode                                Behaviour
  ----------------------------------- -----------------------------------
  Auto (recommended)                  Tries Gemini first; uses local
                                      fallback rules if Gemini is
                                      unavailable.

  Live AI                             Attempts Gemini-powered analysis.
                                      The current application may still
                                      fall back to local rules if the AI
                                      request fails.

  Fallback rules                      Uses local keyword-based
                                      classification and recommendations.

  Demo                                Uses predefined sample tickets from
                                      `demo_data.py`.
  -----------------------------------------------------------------------

AI-generated recommendations are suggestions, not verified diagnoses or
executed fixes. A human support representative should review the
analysis and response draft before taking action.

## Database

The application creates and uses a local SQLite database named
`smartdesk.db` alongside `database.py`. The database is initialised
automatically when the app starts.

The `.gitignore` excludes local database files so personal or test
ticket records are not accidentally committed. The database is created
again when the application runs.

## Privacy and security

-   Use fictional or anonymised ticket descriptions when demonstrating
    the project.
-   Never submit passwords, API keys, authentication tokens, or
    confidential company information.
-   Keep API keys in environment variables or Streamlit secrets, never
    in committed source files.
-   Review AI-generated troubleshooting steps and response drafts before
    using them.

## Current limitations

-   Fallback analysis is keyword/rule-based and may be less flexible
    than Gemini.
-   Gemini availability and usage are subject to API access, quotas, and
    service availability.
-   The SQLite database is local to the environment where the app runs.
    For a multi-user production deployment, use a persistent shared
    database and add appropriate authentication and access controls.
-   Ticket analysis does not automatically send replies or perform
    troubleshooting actions.

## Deployment

The app can be deployed to a Streamlit-compatible hosting platform.
Before deploying:

1.  Push the project source code to GitHub.
2.  Add the required dependencies to `requirements.txt`.
3.  Configure the Gemini API key using the hosting platform's secrets
    manager.
4.  Confirm that the deployment environment provides persistent storage
    if ticket history must survive restarts or redeployments.
5.  Test Auto, Live AI, Fallback rules, ticket status updates, search,
    filters, and CSV exports.

## Author

**Somya Ranjan**

------------------------------------------------------------------------

*SmartDesk AI \| AI-assisted IT Service Desk Automation*
