import json
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from ai_service import analyze_with_gemini
from database import (
    init_db, save_ticket, get_tickets, get_ticket,
    update_ticket_status, update_ticket, delete_ticket,
)
from demo_data import DEMO_TICKETS
from rules import analyze_with_rules

st.set_page_config(
    page_title="SmartDesk AI | IT Helpdesk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ---------- DESIGN SYSTEM ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { --bg:#0b1120; --panel:#111b2e; --panel2:#162238; --line:#263650; --muted:#93a4bd; --text:#edf4ff; --cyan:#43d9d0; --blue:#6da8ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #142b45 0%, #0b1120 42%, #080e19 100%); color:var(--text); }
.block-container { max-width:1500px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#101b2d 0%,#0c1525 100%); border-right:1px solid #263650; }
[data-testid="stSidebar"] * { color:#dce8f8; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:8px 10px; border-radius:10px; }
[data-testid="stMetric"] { background:linear-gradient(145deg,#17263d,#111b2e); border:1px solid #2a3d59; border-radius:16px; padding:17px 19px; box-shadow:0 10px 28px #00000020; }
[data-testid="stMetricLabel"] { color:#9eb0c9 !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#f2f7ff !important; font-family:'Manrope',sans-serif; font-weight:800; }
[data-testid="stMetricDelta"] { font-size:12px; }
div[data-testid="stForm"], div[data-testid="stExpander"] { background:#111b2e; border:1px solid #293b55; border-radius:15px; }
.stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input { background:#101a2b !important; color:#edf4ff !important; border:1px solid #344965 !important; border-radius:10px !important; }
.stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid #3c5878; background:#172a43; color:#edf4ff; font-weight:700; min-height:42px; transition:all .2s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:#43d9d0; color:#43d9d0; background:#1b334e; }
button[kind="primary"] { background:linear-gradient(90deg,#13a99f,#2379c9) !important; border:0 !important; color:white !important; }
hr { border-color:#293b55 !important; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.5px; color:#f4f8ff; }
.eyebrow { color:#43d9d0; text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:800; }
.hero { background:linear-gradient(115deg,#152b45 0%,#14223a 55%,#12333b 100%); border:1px solid #2d5265; border-radius:22px; padding:26px 30px; margin-bottom:24px; box-shadow:0 18px 45px #00000025; }
.hero-title { font-family:'Manrope',sans-serif; font-size:34px; line-height:1.15; font-weight:800; color:#f5f9ff; margin:5px 0 8px; }
.hero-sub { color:#a9bdd5; font-size:14px; }
.panel { background:linear-gradient(145deg,#142138,#101a2b); border:1px solid #293d59; border-radius:17px; padding:19px 21px; }
.panel-title { color:#eaf3ff; font-size:17px; font-weight:800; margin-bottom:12px; }
.muted { color:#94a8c2; font-size:13px; }
.pill { display:inline-block; padding:4px 10px; border-radius:99px; font-size:11px; font-weight:800; border:1px solid #3b526e; background:#1a2b43; color:#cfe0f5; }
.small-note { color:#8fa2bc; font-size:12px; }
[data-testid="stDataFrame"] { border:1px solid #2a3d58; border-radius:12px; overflow:hidden; }
[data-testid="stAlert"] { border-radius:12px; }
footer { visibility:hidden; }
@media(max-width:800px){ .hero-title{font-size:27px;} .block-container{padding-left:1rem;padding-right:1rem;} }
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
STATUSES = ["Open", "In Progress", "Resolved"]
CATEGORIES = ["Software", "Hardware", "Network", "Access", "Security", "Other"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
SENTIMENTS = ["Positive", "Neutral", "Negative"]


def parse_steps(raw):
    try:
        value = json.loads(raw) if isinstance(raw, str) else raw
        return value if isinstance(value, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def prepare_df(records):
    df = pd.DataFrame(records)
    if not df.empty:
        df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["created_date"] = df["created_dt"].dt.date
    return df


def apply_date_filter(df, choice):
    if df.empty or choice == "All time":
        return df
    today = date.today()
    if choice == "Today":
        start = today
    elif choice == "Last 7 days":
        start = today - timedelta(days=6)
    elif choice == "Last 30 days":
        start = today - timedelta(days=29)
    else:
        start = today - timedelta(days=89)
    return df[df["created_date"] >= start]


def metric_card(label, value, note=""):
    st.metric(label, value, note if note else None)


def render_header():
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">AI-powered IT operations</div>
      <div class="hero-title">🎫 SmartDesk <span style="color:#43d9d0">AI</span></div>
      <div class="hero-sub">Intelligent ticket triage · Service desk operations · Actionable insights</div>
    </div>
    """, unsafe_allow_html=True)


def render_ticket_table(records):
    if not records:
        st.info("No tickets match these filters. Try changing your search or filters.")
        return
    df = pd.DataFrame(records)
    view = df[["id", "created_at", "category", "priority", "status", "processing_source", "summary"]].copy()
    view.columns = ["Ticket ID", "Created", "Category", "Priority", "Status", "Processed by", "Issue summary"]
    st.dataframe(view, use_container_width=True, hide_index=True)


def run_analysis(ticket_text, mode, selected_demo=None):
    if mode == "Demo":
        return DEMO_TICKETS[selected_demo]["result"].copy(), "Demo sample"
    if mode == "Fallback rules":
        return analyze_with_rules(ticket_text), "Fallback rules"
    try:
        with st.spinner("SmartDesk AI is analysing the ticket..."):
            result = analyze_with_gemini(ticket_text)
        return result, "Gemini Live AI"
    except Exception as exc:
        if mode == "Live AI":
            st.warning("Gemini could not complete this request. Local fallback rules were used.")
        else:
            st.warning("Gemini is unavailable or its quota may have been reached. Local fallback rules were used.")
        st.caption(f"Technical detail: {str(exc)[:240]}")
        return analyze_with_rules(ticket_text), "Fallback rules"


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<div style='font-size:25px;font-weight:800;font-family:Manrope'>🎫 SmartDesk <span style='color:#43d9d0'>AI</span></div>", unsafe_allow_html=True)
    st.caption("IT SERVICE MANAGEMENT")
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Analyze ticket", "Ticket management", "Analytics"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**⚙️ AI configuration**")
    mode = st.radio(
        "Processing mode",
        ["Auto (recommended)", "Live AI", "Fallback rules", "Demo"],
        index=0,
        help="Auto tries Gemini first and switches to local rules if Gemini is unavailable.",
    )
    st.markdown("<div class='small-note'>🔒 Use fictional or anonymised ticket data. Never enter passwords, API keys or confidential information.</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='small-note'>SMARTDESK AI · VERSION 2.0<br>AI suggestions require human review.</div>", unsafe_allow_html=True)

render_header()
all_tickets = get_tickets()
all_df = prepare_df(all_tickets)

# ---------- OVERVIEW ----------
if page == "Overview":
    st.markdown("<div class='eyebrow'>Workspace / Overview</div>", unsafe_allow_html=True)
    st.title("Service desk overview")
    st.caption("A real-time snapshot of support activity stored in your local SQLite database.")
    period = st.selectbox("Reporting period", ["All time", "Today", "Last 7 days", "Last 30 days", "Last 90 days"], index=0)
    df = apply_date_filter(all_df, period)
    records = df.to_dict("records") if not df.empty else []
    total = len(df)
    open_count = int((df["status"] == "Open").sum()) if total else 0
    progress_count = int((df["status"] == "In Progress").sum()) if total else 0
    critical_count = int((df["priority"] == "Critical").sum()) if total else 0
    resolved_count = int((df["status"] == "Resolved").sum()) if total else 0
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: metric_card("Total tickets", total)
    with m2: metric_card("Open", open_count)
    with m3: metric_card("In progress", progress_count)
    with m4: metric_card("Critical", critical_count)
    with m5: metric_card("Resolved", resolved_count)
    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("<div class='panel'><div class='panel-title'>Recent support tickets</div><div class='muted'>Latest activity across your service desk</div></div>", unsafe_allow_html=True)
        render_ticket_table(records[:8])
    with right:
        st.markdown("<div class='panel'><div class='panel-title'>Ticket status</div><div class='muted'>Current workload distribution</div></div>", unsafe_allow_html=True)
        if total:
            status_counts = df["status"].value_counts().reindex(STATUSES, fill_value=0)
            st.bar_chart(status_counts, use_container_width=True)
        else:
            st.info("Status insights will appear after tickets are analysed.")
    st.write("")
    a, b = st.columns(2)
    with a:
        st.markdown("<div class='panel-title'>Priority breakdown</div>", unsafe_allow_html=True)
        if total:
            st.bar_chart(df["priority"].value_counts().reindex(PRIORITIES, fill_value=0), use_container_width=True)
        else: st.info("No priority data yet.")
    with b:
        st.markdown("<div class='panel-title'>Tickets by category</div>", unsafe_allow_html=True)
        if total:
            st.bar_chart(df["category"].value_counts(), use_container_width=True)
        else: st.info("No category data yet.")

# ---------- ANALYZE TICKET ----------
elif page == "Analyze ticket":
    st.markdown("<div class='eyebrow'>Workspace / New request</div>", unsafe_allow_html=True)
    st.title("Analyze a support ticket")
    st.caption("Turn an unstructured issue report into a structured, actionable support ticket.")
    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        st.markdown("<div class='panel-title'>📥 Ticket details</div>", unsafe_allow_html=True)
        selected_demo = None
        default_ticket = ""
        if mode == "Demo":
            selected_demo = st.selectbox("Choose a sample ticket", list(DEMO_TICKETS.keys()))
            default_ticket = DEMO_TICKETS[selected_demo]["ticket"]
        ticket_text = st.text_area(
            "Customer issue description", value=default_ticket,
            placeholder="Example: I cannot access the company VPN since this morning...",
            height=190, key="new_ticket_text",
        )
        analyze_clicked = st.button("✨ Analyze ticket", type="primary", use_container_width=True)
    with right:
        st.markdown("<div class='panel-title'>🧠 What SmartDesk AI does</div>", unsafe_allow_html=True)
        for line in ["Classifies the incoming request", "Estimates urgency and priority", "Creates a concise issue summary", "Recommends safe first troubleshooting steps", "Drafts a professional support response"]:
            st.markdown(f"<div style='padding:8px 0;border-bottom:1px solid #263650;color:#c5d5e9'>✦ &nbsp;{line}</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='small-note'>AI-generated recommendations must be reviewed by a human support agent. SmartDesk does not send replies or execute fixes.</div>", unsafe_allow_html=True)
    if analyze_clicked:
        if not ticket_text.strip():
            st.warning("Please enter a ticket description first.")
        else:
            result, source = run_analysis(ticket_text, mode, selected_demo)
            ticket_id = save_ticket(ticket_text, result, source)
            st.session_state["last_ticket_id"] = ticket_id
            st.success(f"Ticket #{ticket_id} analysed and saved successfully.")
            st.rerun()
    last_id = st.session_state.get("last_ticket_id")
    if last_id:
        last = get_ticket(last_id)
        if last:
            st.divider()
            st.subheader(f"Latest analysis · Ticket #{last_id}")
            q1, q2, q3, q4 = st.columns(4)
            q1.metric("Category", last["category"])
            q2.metric("Priority", last["priority"])
            q3.metric("Sentiment", last["sentiment"])
            q4.metric("Status", last["status"])
            st.markdown("**Issue summary**")
            st.write(last["summary"])
            x, y = st.columns(2)
            with x:
                st.markdown("**Suggested troubleshooting**")
                for step in parse_steps(last["troubleshooting_steps"]): st.markdown(f"- {step}")
            with y:
                st.markdown("**Draft response**")
                st.text_area("Review before sending", value=last["response_draft"], height=190, key=f"latest_response_{last_id}")
            st.caption(f"Processing source: {last['processing_source']} · Human review required")
            export = pd.DataFrame([last]).drop(columns=["troubleshooting_steps"], errors="ignore")
            st.download_button("⬇️ Download ticket record (CSV)", export.to_csv(index=False).encode("utf-8"), f"smartdesk_ticket_{last_id}.csv", "text/csv")

# ---------- TICKET MANAGEMENT ----------
elif page == "Ticket management":
    st.markdown("<div class='eyebrow'>Workspace / Operations</div>", unsafe_allow_html=True)
    st.title("Ticket management")
    st.caption("Search, filter, inspect, update and remove support tickets.")
    search = st.text_input("🔎 Search tickets", placeholder="Search by ticket ID, issue description or summary...")
    f1, f2, f3, f4 = st.columns(4)
    with f1: category_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with f2: priority_filter = st.selectbox("Priority", ["All"] + PRIORITIES)
    with f3: status_filter = st.selectbox("Status", ["All"] + STATUSES)
    with f4: ticket_period = st.selectbox("Created", ["All time", "Today", "Last 7 days", "Last 30 days", "Last 90 days"])
    filtered = all_tickets.copy()
    if ticket_period != "All time":
        filtered_df = apply_date_filter(prepare_df(filtered), ticket_period)
        filtered = filtered_df.to_dict("records") if not filtered_df.empty else []
    if search.strip():
        term = search.strip().lower()
        filtered = [t for t in filtered if term in str(t["id"]).lower() or term in t["ticket_text"].lower() or term in t["summary"].lower()]
    if category_filter != "All": filtered = [t for t in filtered if t["category"] == category_filter]
    if priority_filter != "All": filtered = [t for t in filtered if t["priority"] == priority_filter]
    if status_filter != "All": filtered = [t for t in filtered if t["status"] == status_filter]
    st.divider()
    st.subheader(f"Matching tickets · {len(filtered)}")
    render_ticket_table(filtered)
    if filtered:
        selected_id = st.selectbox("Select a ticket to inspect", [t["id"] for t in filtered], format_func=lambda x: f"Ticket #{x}")
        selected = get_ticket(selected_id)
        if selected:
            st.divider()
            st.subheader(f"Ticket #{selected_id} details")
            st.markdown("<div class='panel'><div class='muted'>CUSTOMER ISSUE</div></div>", unsafe_allow_html=True)
            st.write(selected["ticket_text"])
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Category", selected["category"])
            p2.metric("Priority", selected["priority"])
            p3.metric("Status", selected["status"])
            p4.metric("Sentiment", selected["sentiment"])
            st.markdown("**Issue summary**")
            st.write(selected["summary"])
            st.markdown("**Troubleshooting steps**")
            for step in parse_steps(selected["troubleshooting_steps"]): st.markdown(f"- {step}")
            with st.expander("✏️ Edit ticket information", expanded=False):
                with st.form(f"edit_ticket_{selected_id}"):
                    edited_text = st.text_area("Issue description", selected["ticket_text"], height=110)
                    e1, e2, e3 = st.columns(3)
                    with e1: edited_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(selected["category"]) if selected["category"] in CATEGORIES else CATEGORIES.index("Other"))
                    with e2: edited_priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(selected["priority"]) if selected["priority"] in PRIORITIES else 2)
                    with e3: edited_sentiment = st.selectbox("Sentiment", SENTIMENTS, index=SENTIMENTS.index(selected["sentiment"]) if selected["sentiment"] in SENTIMENTS else 1)
                    edited_summary = st.text_area("Issue summary", selected["summary"], height=90)
                    steps_text = st.text_area("Troubleshooting steps (one per line)", "\n".join(parse_steps(selected["troubleshooting_steps"])), height=120)
                    edited_response = st.text_area("Draft response", selected["response_draft"], height=160)
                    save_edit = st.form_submit_button("Save changes", type="primary", use_container_width=True)
                if save_edit:
                    update_ticket(selected_id, edited_text, edited_category, edited_priority, edited_sentiment, edited_summary, [s.strip() for s in steps_text.splitlines() if s.strip()], edited_response)
                    st.success("Ticket updated successfully.")
                    st.rerun()
            s1, s2 = st.columns([1, 2])
            with s1:
                new_status = st.selectbox("Update status", STATUSES, index=STATUSES.index(selected["status"]) if selected["status"] in STATUSES else 0, key=f"manage_status_{selected_id}")
                if st.button("Save status", key=f"manage_save_status_{selected_id}"):
                    update_ticket_status(selected_id, new_status)
                    st.success("Ticket status updated.")
                    st.rerun()
            with s2:
                with st.expander("🗑️ Delete ticket", expanded=False):
                    st.warning("This permanently deletes the selected ticket from the local SQLite database.")
                    confirm_delete = st.checkbox(f"I understand. Delete ticket #{selected_id} permanently.", key=f"confirm_delete_{selected_id}")
                    if st.button("Delete this ticket", disabled=not confirm_delete, key=f"delete_{selected_id}"):
                        delete_ticket(selected_id)
                        if st.session_state.get("last_ticket_id") == selected_id:
                            del st.session_state["last_ticket_id"]
                        st.success(f"Ticket #{selected_id} deleted.")
                        st.rerun()
    if filtered:
        export_df = pd.DataFrame(filtered).drop(columns=["troubleshooting_steps"], errors="ignore")
        st.download_button("⬇️ Export matching tickets as CSV", export_df.to_csv(index=False).encode("utf-8"), "smartdesk_filtered_tickets.csv", "text/csv", use_container_width=True)

# ---------- ANALYTICS ----------
elif page == "Analytics":
    st.markdown("<div class='eyebrow'>Workspace / Insights</div>", unsafe_allow_html=True)
    st.title("Ticket analytics")
    st.caption("Understand ticket volume, urgency, workload and AI processing activity.")
    period = st.selectbox("Analytics period", ["All time", "Today", "Last 7 days", "Last 30 days", "Last 90 days"], index=0, key="analytics_period")
    df = apply_date_filter(all_df, period)
    if df.empty:
        st.info("Analytics will appear after tickets have been analysed in the selected period.")
    else:
        a, b, c, d = st.columns(4)
        a.metric("Tickets analysed", len(df))
        b.metric("Average priority score", round(df["priority"].map({"Critical":4,"High":3,"Medium":2,"Low":1}).mean(), 2))
        c.metric("Resolved", int((df["status"] == "Resolved").sum()))
        d.metric("AI processed", int(df["processing_source"].astype(str).str.contains("Gemini", case=False).sum()))
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Tickets by category")
            st.bar_chart(df["category"].value_counts(), use_container_width=True)
        with c2:
            st.subheader("Priority distribution")
            st.bar_chart(df["priority"].value_counts().reindex(PRIORITIES, fill_value=0), use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Status distribution")
            st.bar_chart(df["status"].value_counts().reindex(STATUSES, fill_value=0), use_container_width=True)
        with c4:
            st.subheader("Processing source")
            st.bar_chart(df["processing_source"].value_counts(), use_container_width=True)
        st.divider()
        st.subheader("Ticket volume over time")
        daily = df.dropna(subset=["created_dt"]).copy()
        if not daily.empty:
            daily_counts = daily.set_index("created_dt").resample("D").size().rename("Tickets")
            st.area_chart(daily_counts, use_container_width=True)
        else:
            st.caption("No valid timestamps available for the selected period.")
        st.download_button("⬇️ Export analytics data", df.drop(columns=["created_dt", "created_date"], errors="ignore").to_csv(index=False).encode("utf-8"), "smartdesk_analytics.csv", "text/csv")

st.divider()
st.markdown("<div class='small-note'>© 2026 SmartDesk AI · Intelligent IT Support Automation · AI-generated recommendations require human review.</div>", unsafe_allow_html=True)
