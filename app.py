import streamlit as st
import os
import time
from math import pi
from urllib.parse import quote
from datetime import datetime
from utils.extract_text import extract_text
from utils.extract_skills import extract_skills
from utils.extract_experience import extract_experience
from utils.compare import compare_skills, compare_experience

st.set_page_config(
    page_title="Smart Resume Matcher | AI Screening Tool",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# =====================================================================
# Helpers: icons, HTML rendering
# =====================================================================
ICONS = {
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    "file-text": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "plus-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
    "circle": '<circle cx="12" cy="12" r="10"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "bar-chart": '<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "upload-cloud": '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "sun": '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>',
    "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "grid": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
}


def icon(name, size=18):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" style="vertical-align:middle;flex-shrink:0">{ICONS[name]}</svg>'
    )


def mask_url(name):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        f'fill="none" stroke="black" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</svg>'
    )
    return f'url("data:image/svg+xml;utf8,{quote(svg, safe="")}")'


def _h(s):
    """Strip indentation and blank lines so Streamlit's markdown keeps HTML as one block."""
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def render(s):
    st.markdown(_h(s), unsafe_allow_html=True)


def section_title(icon_name, text, sub=None):
    sub_html = f'<p class="section-sub">{sub}</p>' if sub else ""
    render(f"""
    <div class="section-head">
        <div class="section-icon">{icon(icon_name, 18)}</div>
        <div>
            <p class="section-heading">{text}</p>
            {sub_html}
        </div>
    </div>
    """)


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fmt(n):
    return str(int(n)) if n == int(n) else f"{n:.1f}"


# =====================================================================
# Theme (light / dark)
# =====================================================================
LIGHT = {
    "bg": "#f5f7fb", "card": "#ffffff", "border": "#e5e9f2", "text": "#0f172a",
    "soft": "#475569", "muted": "#94a3b8", "primary": "#4f46e5", "primary-dark": "#4338ca",
    "primary-soft": "#eef2ff", "input": "#f8faff", "track": "#e8ecf4", "sidebar": "#ffffff",
    "shadow": "0 1px 2px rgba(16,24,40,0.04), 0 6px 20px rgba(16,24,40,0.06)",
    "good-bg": "#ecfdf5", "good-bd": "#a7f3d0", "good-tx": "#047857",
    "warn-bg": "#fffbeb", "warn-bd": "#fde68a", "warn-tx": "#92400e",
    "bad-bg": "#fff1f2", "bad-bd": "#fecdd3", "bad-tx": "#be123c",
    "info-bg": "#eef2ff", "info-bd": "#c7d2fe", "info-tx": "#3730a3",
    "neutral-bg": "#f1f5f9", "neutral-bd": "#e2e8f0", "neutral-tx": "#475569",
}
DARK = {
    "bg": "#0b1020", "card": "#131a2e", "border": "#243049", "text": "#e6ebf5",
    "soft": "#a7b3c9", "muted": "#6b7a96", "primary": "#818cf8", "primary-dark": "#6366f1",
    "primary-soft": "#1e2447", "input": "#0f1629", "track": "#243049", "sidebar": "#0e1426",
    "shadow": "0 1px 2px rgba(0,0,0,0.3), 0 8px 24px rgba(0,0,0,0.35)",
    "good-bg": "rgba(16,185,129,0.12)", "good-bd": "rgba(16,185,129,0.35)", "good-tx": "#6ee7b7",
    "warn-bg": "rgba(245,158,11,0.12)", "warn-bd": "rgba(245,158,11,0.35)", "warn-tx": "#fcd34d",
    "bad-bg": "rgba(244,63,94,0.12)", "bad-bd": "rgba(244,63,94,0.35)", "bad-tx": "#fda4af",
    "info-bg": "rgba(129,140,248,0.14)", "info-bd": "rgba(129,140,248,0.35)", "info-tx": "#c7d2fe",
    "neutral-bg": "rgba(148,163,184,0.10)", "neutral-bd": "rgba(148,163,184,0.25)", "neutral-tx": "#cbd5e1",
}

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

# ---------------- Sidebar (built first so the theme toggle value is known) ----------------
with st.sidebar:
    render(f"""
    <div class="brand">
        <div class="brand-logo">{icon("cpu", 20)}</div>
        <div>
            <p class="brand-name">Smart Resume Matcher</p>
            <p class="brand-sub">Recruitment Suite</p>
        </div>
    </div>
    """)

    st.markdown('<p class="side-label">Menu</p>', unsafe_allow_html=True)
    page = st.radio("Navigation", ["Analyzer", "Guide"], label_visibility="collapsed", key="nav")

    st.markdown('<p class="side-label">Appearance</p>', unsafe_allow_html=True)
    dark = st.toggle("Dark mode", key="dark_mode")

    st.markdown('<p class="side-label">About</p>', unsafe_allow_html=True)
    render(f"""
    <div class="side-card">
        <p>Screens a candidate's resume against a job description and generates a compatibility
        report with matched skills, missing skills and experience fit.</p>
    </div>
    """)
    st.markdown('<p class="side-label">How to use</p>', unsafe_allow_html=True)
    render("""
    <div class="side-card">
        <p><b>1.</b> Upload the candidate's resume<br>
        <b>2.</b> Paste the job description<br>
        <b>3.</b> Click <b>Analyze</b><br>
        <b>4.</b> Review the compatibility report</p>
    </div>
    """)
    st.caption("Built with Python & Streamlit")

palette = DARK if dark else LIGHT
theme_vars = ":root{" + "".join(f"--{k}:{v};" for k, v in palette.items()) + "}"

nav_icons_css = f"""
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-child(1)::before {{ -webkit-mask-image: {mask_url("grid")}; mask-image: {mask_url("grid")}; }}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-child(2)::before {{ -webkit-mask-image: {mask_url("book-open")}; mask-image: {mask_url("book-open")}; }}
"""

# =====================================================================
# Custom CSS
# =====================================================================
STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, button, input, textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stApp, [data-testid="stAppViewContainer"] { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
.block-container { padding-top: 3.2rem !important; padding-bottom: 3rem !important; max-width: 1240px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes grow { from { width: 0; } }
@keyframes ringfill { from { stroke-dashoffset: var(--circ); } to { stroke-dashoffset: var(--off); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .45; } }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--sidebar); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 1.2rem; }
.brand { display: flex; align-items: center; gap: 12px; padding: 4px 4px 12px 4px; }
.brand-logo {
    width: 40px; height: 40px; border-radius: 11px; color: #fff;
    background: linear-gradient(135deg, #6366f1, #4338ca);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 14px rgba(79,70,229,.35);
}
.brand-name { font-size: 15px; font-weight: 700; color: var(--text); margin: 0; line-height: 1.2; }
.brand-sub { font-size: 12px; color: var(--muted); margin: 0; }
.side-label {
    font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
    color: var(--muted) !important; margin: 18px 0 8px 4px;
}
.side-card {
    background: var(--input); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px;
}
.side-card p { font-size: 12.5px; line-height: 1.65; color: var(--soft) !important; margin: 0; }
.side-card b { color: var(--text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--muted); margin-top: 14px; }

[data-testid="stSidebar"] [role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
    display: flex; align-items: center; gap: 10px; width: 100%;
    padding: 10px 12px; border-radius: 10px; cursor: pointer; transition: background .15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] > label::before {
    content: ""; width: 18px; height: 18px; flex-shrink: 0; background-color: currentColor;
    -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
    -webkit-mask-position: center; mask-position: center;
    -webkit-mask-size: contain; mask-size: contain;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover { background: var(--primary-soft); }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) { background: var(--primary-soft); color: var(--primary); }
[data-testid="stSidebar"] [role="radiogroup"] > label p { font-weight: 600; font-size: 14px; color: inherit !important; }

/* ---------- Top navbar ---------- */
.navbar {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
    background: var(--card); border: 1px solid var(--border); border-radius: 14px;
    padding: 12px 20px; box-shadow: var(--shadow); margin-bottom: 22px; animation: fadeUp .4s ease;
}
.crumbs { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); }
.crumbs b { color: var(--text); font-weight: 600; }
.nav-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.nav-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--primary-soft); color: var(--primary) !important;
    font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 999px;
}
.nav-pill.plain { background: var(--neutral-bg); color: var(--neutral-tx) !important; }

/* ---------- Page header ---------- */
.page-title { font-size: 26px; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -.02em; }
.page-sub { font-size: 14px; color: var(--soft); margin: 4px 0 20px 0; }

/* ---------- Cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card); border: 1px solid var(--border) !important;
    border-radius: 14px !important; box-shadow: var(--shadow); padding: 10px 14px;
    animation: fadeUp .45s ease;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] { box-shadow: none; }

.section-head { display: flex; align-items: center; gap: 12px; margin: 4px 0 16px 0; }
.section-icon {
    width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
    background: var(--primary-soft); color: var(--primary);
    display: flex; align-items: center; justify-content: center;
}
.section-heading { font-size: 16px; font-weight: 600; color: var(--text) !important; margin: 0; line-height: 1.3; }
.section-sub { font-size: 12.5px; color: var(--muted) !important; margin: 2px 0 0 0; }
.sub-heading {
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    font-size: 12px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
    color: var(--soft) !important; margin-bottom: 12px;
}
.count-pill {
    background: var(--neutral-bg); color: var(--neutral-tx) !important; border-radius: 999px;
    padding: 2px 9px; font-size: 11.5px; letter-spacing: 0; text-transform: none;
}
.body-text { font-size: 14px; color: var(--soft) !important; line-height: 1.6; margin: 0; }

/* ---------- Inputs ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stCheckbox"] p, label p {
    color: var(--text) !important; font-weight: 600; font-size: 14px;
}
[data-testid="stFileUploaderDropzone"] {
    background: var(--input); border: 2px dashed var(--info-bd); border-radius: 12px;
    padding: 28px; transition: all .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover { background: var(--primary-soft); border-color: var(--primary); }
[data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploaderFile"] * { color: var(--soft) !important; }
[data-testid="stFileUploaderDropzone"] button {
    border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--text) !important;
}
[data-testid="stFileUploaderDropzone"] button * { color: var(--text) !important; }
.stTextArea textarea {
    background: var(--input) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 12px !important;
    font-size: 14px; padding: 14px;
}
.stTextArea textarea:focus {
    border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(99,102,241,.18) !important;
}
.stTextArea textarea::placeholder { color: var(--muted) !important; }
[data-testid="stAlert"] { border-radius: 12px; }

/* ---------- Buttons ---------- */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff !important; border: none;
    border-radius: 10px; padding: 12px 24px; font-weight: 600; font-size: 15px;
    box-shadow: 0 6px 16px rgba(79,70,229,.32); transition: all .2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #4338ca); transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(79,70,229,.42); color: #fff !important;
}
.stButton > button p { color: #fff !important; }
.stDownloadButton > button {
    background: var(--card); color: var(--primary) !important; border: 1.5px solid var(--primary);
    border-radius: 10px; padding: 12px 24px; font-weight: 600; font-size: 15px; transition: all .2s ease;
}
.stDownloadButton > button:hover { background: var(--primary-soft); border-color: var(--primary-dark); }
.stDownloadButton > button p { color: var(--primary) !important; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--border); }
.stTabs button[data-baseweb="tab"] { padding: 10px 16px; border-radius: 8px 8px 0 0; }
.stTabs button[data-baseweb="tab"] p { color: var(--soft) !important; font-weight: 600; font-size: 14px; }
.stTabs button[data-baseweb="tab"][aria-selected="true"] p { color: var(--primary) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--primary) !important; }
.stTabs [data-baseweb="tab-border"] { background-color: transparent !important; }

/* ---------- Metric cards ---------- */
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 6px 0 18px 0; }
@media (max-width: 1000px) { .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.metric {
    display: flex; align-items: center; gap: 14px; background: var(--card);
    border: 1px solid var(--border); border-radius: 14px; padding: 18px; box-shadow: var(--shadow);
    animation: fadeUp .45s ease; transition: transform .2s ease;
}
.metric:hover { transform: translateY(-2px); }
.metric-icon {
    width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
.tone-good { background: var(--good-bg); color: var(--good-tx); }
.tone-warn { background: var(--warn-bg); color: var(--warn-tx); }
.tone-bad { background: var(--bad-bg); color: var(--bad-tx); }
.tone-info { background: var(--info-bg); color: var(--info-tx); }
.tone-neutral { background: var(--neutral-bg); color: var(--neutral-tx); }
.metric-label { font-size: 12.5px; color: var(--soft) !important; margin: 0; font-weight: 500; }
.metric-value { font-size: 26px; font-weight: 700; color: var(--text) !important; margin: 2px 0; line-height: 1.15; letter-spacing: -.02em; }
.metric-sub { font-size: 12px; color: var(--muted) !important; margin: 0; }

/* ---------- Score ring ---------- */
.ring-wrap { position: relative; width: 190px; height: 190px; margin: 6px auto 4px auto; }
.ring { width: 100%; height: 100%; }
.ring-track { stroke: var(--track); }
.ring-progress { animation: ringfill 1.2s ease-out forwards; }
.ring-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-number { font-size: 40px; font-weight: 700; letter-spacing: -.03em; line-height: 1.1; }
.ring-label { font-size: 12px; font-weight: 500; color: var(--soft); margin-top: 2px; }

/* ---------- Progress / charts ---------- */
.bar-row { margin-bottom: 18px; }
.bar-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.bar-name { font-size: 13px; font-weight: 600; color: var(--text) !important; margin: 0; }
.bar-val { font-size: 13px; font-weight: 600; color: var(--soft) !important; margin: 0; }
.progress { height: 10px; background: var(--track); border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 999px; animation: grow .9s ease-out; }
.stack { display: flex; height: 14px; border-radius: 999px; overflow: hidden; background: var(--track); }
.stack > div { height: 100%; animation: grow .9s ease-out; }
.legend { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 10px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--soft); }
.legend i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }

/* ---------- Badges & pills ---------- */
.badge-match, .badge-missing, .badge-extra {
    display: inline-block; padding: 5px 13px; border-radius: 999px; margin: 4px 6px 4px 0;
    font-size: 13px; font-weight: 500;
}
.badge-match { background: var(--good-bg); color: var(--good-tx) !important; border: 1px solid var(--good-bd); }
.badge-missing { background: var(--bad-bg); color: var(--bad-tx) !important; border: 1px solid var(--bad-bd); }
.badge-extra { background: var(--neutral-bg); color: var(--neutral-tx) !important; border: 1px solid var(--neutral-bd); }
.pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.pill-good { background: var(--good-bg); color: var(--good-tx) !important; border: 1px solid var(--good-bd); }
.pill-bad { background: var(--bad-bg); color: var(--bad-tx) !important; border: 1px solid var(--bad-bd); }

.req-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 4px; border-bottom: 1px solid var(--border);
}
.req-row:last-child { border-bottom: none; }
.req-name { font-size: 14px; font-weight: 500; color: var(--text) !important; margin: 0; }

/* ---------- Banners ---------- */
.banner-strong, .banner-moderate, .banner-weak, .banner-info {
    padding: 14px 18px; border-radius: 12px; font-weight: 500; font-size: 14px; line-height: 1.55; margin-top: 12px;
}
.banner-strong { background: var(--good-bg); color: var(--good-tx) !important; border: 1px solid var(--good-bd); border-left: 5px solid #10b981; }
.banner-moderate { background: var(--warn-bg); color: var(--warn-tx) !important; border: 1px solid var(--warn-bd); border-left: 5px solid #f59e0b; }
.banner-weak { background: var(--bad-bg); color: var(--bad-tx) !important; border: 1px solid var(--bad-bd); border-left: 5px solid #f43f5e; }
.banner-info { background: var(--info-bg); color: var(--info-tx) !important; border: 1px solid var(--info-bd); border-left: 5px solid #6366f1; }

.explanation-box, .recommend-box {
    background: var(--input); border: 1px solid var(--border); border-left: 4px solid var(--primary);
    padding: 18px 22px; border-radius: 12px; color: var(--text) !important; font-size: 14px; line-height: 1.75;
}
.explanation-box b, .recommend-box b { color: var(--text); font-weight: 600; }
.recommend-box ul { margin: 8px 0 0 0; padding-left: 20px; }
.recommend-box li { margin-bottom: 4px; }

/* ---------- Result header ---------- */
.result-head {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
    margin: 26px 0 14px 0;
}
.result-title { font-size: 20px; font-weight: 700; color: var(--text) !important; margin: 0; letter-spacing: -.01em; }
.result-sub { font-size: 13px; color: var(--muted) !important; margin: 2px 0 0 0; }

/* ---------- Loader ---------- */
.loader-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 14px; box-shadow: var(--shadow);
    padding: 30px; margin-top: 18px; text-align: center; animation: fadeUp .3s ease;
}
.spinner {
    width: 46px; height: 46px; border-radius: 50%; margin: 0 auto 16px auto;
    border: 4px solid var(--track); border-top-color: var(--primary); animation: spin .8s linear infinite;
}
.loader-title { font-size: 16px; font-weight: 600; color: var(--text) !important; margin: 0; }
.loader-sub { font-size: 13px; color: var(--muted) !important; margin: 4px 0 18px 0; }
.loader-card .progress { max-width: 420px; margin: 0 auto 18px auto; }
.steps { display: inline-flex; flex-direction: column; gap: 10px; text-align: left; }
.step { display: flex; align-items: center; gap: 10px; font-size: 13.5px; }
.step.done { color: var(--good-tx); }
.step.active { color: var(--text); font-weight: 600; animation: pulse 1.2s ease infinite; }
.step.todo { color: var(--muted); }
.dot-spin {
    width: 14px; height: 14px; border-radius: 50%; display: inline-block; flex-shrink: 0;
    border: 2px solid var(--track); border-top-color: var(--primary); animation: spin .7s linear infinite;
}

/* ---------- Empty state ---------- */
.empty {
    background: var(--card); border: 1px dashed var(--info-bd); border-radius: 14px;
    padding: 40px 24px; text-align: center; margin-top: 22px; animation: fadeUp .5s ease;
}
.empty-icon {
    width: 72px; height: 72px; border-radius: 20px; margin: 0 auto 16px auto;
    background: var(--primary-soft); color: var(--primary); display: flex; align-items: center; justify-content: center;
}
.empty-title { font-size: 18px; font-weight: 700; color: var(--text) !important; margin: 0; }
.empty-sub { font-size: 14px; color: var(--soft) !important; margin: 6px auto 18px auto; max-width: 460px; line-height: 1.6; }
.checklist { display: inline-flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-bottom: 26px; }
.check { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; }
.check.ok { background: var(--good-bg); color: var(--good-tx); border: 1px solid var(--good-bd); }
.check.wait { background: var(--neutral-bg); color: var(--neutral-tx); border: 1px solid var(--neutral-bd); }
.feature-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; text-align: left; }
@media (max-width: 900px) { .feature-grid { grid-template-columns: 1fr; } }
.feature { background: var(--input); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.feature .metric-icon { width: 38px; height: 38px; margin-bottom: 10px; }
.feature-title { font-size: 14px; font-weight: 600; color: var(--text) !important; margin: 0 0 4px 0; }
.feature-text { font-size: 12.5px; color: var(--soft) !important; margin: 0; line-height: 1.55; }

/* ---------- Guide ---------- */
.guide-steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 900px) { .guide-steps { grid-template-columns: 1fr; } }
.guide-step { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; box-shadow: var(--shadow); }
.guide-num {
    width: 30px; height: 30px; border-radius: 50%; background: var(--primary); color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; margin-bottom: 12px;
}

/* ---------- Footer ---------- */
.footer { text-align: center; color: var(--muted); font-size: 12px; margin-top: 44px; padding-top: 18px; border-top: 1px solid var(--border); }
"""

st.markdown(f"<style>{theme_vars}{STATIC_CSS}{nav_icons_css}</style>", unsafe_allow_html=True)

# =====================================================================
# Top navbar
# =====================================================================
theme_icon = icon("moon", 14) if dark else icon("sun", 14)
theme_name = "Dark" if dark else "Light"
render(f"""
<div class="navbar">
    <div class="crumbs">
        {icon("layers", 16)}
        <span>Workspace</span><span>/</span><span>Resume Screening</span><span>/</span><b>{page}</b>
    </div>
    <div class="nav-right">
        <span class="nav-pill plain">{theme_icon}{theme_name} mode</span>
        <span class="nav-pill">{icon("zap", 14)}AI Screening</span>
    </div>
</div>
""")

# =====================================================================
# Loader
# =====================================================================
STEPS = ["Reading resume", "Extracting skills", "Checking experience", "Scoring compatibility"]


def loader_html(active):
    rows = ""
    for i, label in enumerate(STEPS):
        if i < active:
            cls, ic = "done", icon("check-circle", 16)
        elif i == active:
            cls, ic = "active", '<span class="dot-spin"></span>'
        else:
            cls, ic = "todo", icon("circle", 16)
        rows += f'<div class="step {cls}">{ic}<span>{label}</span></div>'
    pct = int(active / len(STEPS) * 100)
    return _h(f"""
    <div class="loader-card">
        <div class="spinner"></div>
        <p class="loader-title">Analyzing candidate profile</p>
        <p class="loader-sub">This only takes a moment</p>
        <div class="progress"><div class="progress-fill" style="width:{pct}%;background:var(--primary)"></div></div>
        <div class="steps">{rows}</div>
    </div>
    """)


def score_ring(score, color):
    s = max(0.0, min(100.0, float(score)))
    r = 54
    circ = 2 * pi * r
    off = circ * (1 - s / 100)
    return _h(f"""
    <div class="ring-wrap">
        <svg viewBox="0 0 140 140" class="ring">
            <circle class="ring-track" cx="70" cy="70" r="{r}" fill="none" stroke-width="12"/>
            <circle class="ring-progress" cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="12"
                stroke-linecap="round" stroke-dasharray="{circ:.2f}" stroke-dashoffset="{off:.2f}"
                transform="rotate(-90 70 70)" style="--circ:{circ:.2f};--off:{off:.2f}"/>
        </svg>
        <div class="ring-center">
            <div class="ring-number" style="color:{color}">{score}%</div>
            <div class="ring-label">Match score</div>
        </div>
    </div>
    """)


def metric_card(icon_name, label, value, sub, tone):
    return f"""
    <div class="metric">
        <div class="metric-icon tone-{tone}">{icon(icon_name, 22)}</div>
        <div>
            <p class="metric-label">{label}</p>
            <p class="metric-value">{value}</p>
            <p class="metric-sub">{sub}</p>
        </div>
    </div>
    """


# =====================================================================
# Page: Guide
# =====================================================================
if page == "Guide":
    render("""
    <p class="page-title">Guide</p>
    <p class="page-sub">Everything you need to screen a candidate in under a minute.</p>
    """)
    render(f"""
    <div class="guide-steps">
        <div class="guide-step">
            <div class="guide-num">1</div>
            <p class="feature-title">{icon("upload-cloud", 16)}&nbsp; Upload the resume</p>
            <p class="feature-text">Add the candidate's resume as a PDF or DOCX file.</p>
        </div>
        <div class="guide-step">
            <div class="guide-num">2</div>
            <p class="feature-title">{icon("briefcase", 16)}&nbsp; Paste the job description</p>
            <p class="feature-text">Paste the full job description so required skills and experience can be detected.</p>
        </div>
        <div class="guide-step">
            <div class="guide-num">3</div>
            <p class="feature-title">{icon("bar-chart", 16)}&nbsp; Review the report</p>
            <p class="feature-text">Check the match score, skill gaps, experience fit and recommendations, then download the report.</p>
        </div>
    </div>
    """)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        section_title("target", "Understanding the match score", "How the verdict is decided")
        render("""
        <div class="req-row"><p class="req-name">75% and above</p><span class="pill pill-good">Strong match</span></div>
        <div class="req-row"><p class="req-name">50% to 74%</p><span class="badge-extra" style="margin:0">Moderate match</span></div>
        <div class="req-row"><p class="req-name">Below 50%</p><span class="pill pill-bad">Weak match</span></div>
        """)
    render('<div class="footer">Smart Resume Matcher © 2026 | Internal Recruitment Tool</div>')
    st.stop()

# =====================================================================
# Page: Analyzer
# =====================================================================
render("""
<p class="page-title">Candidate Screening</p>
<p class="page-sub">AI-powered resume screening and job compatibility analysis for recruiters.</p>
""")

# ---------------- Input Section ----------------
with st.container(border=True):
    section_title("upload-cloud", "Step 1: Upload Documents", "Add a resume and the job description to begin")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        resume_file = st.file_uploader("Candidate Resume (PDF or DOCX)", type=["pdf", "docx"])
    with col2:
        jd_text = st.text_area("Job Description", height=200, placeholder="Paste the full job description here...")

    analyze_btn = st.button("🔍 Analyze Compatibility", use_container_width=True, type="primary")

loader_slot = st.empty()

# ---------------- Analysis (logic unchanged) ----------------
if analyze_btn:
    if resume_file is None or jd_text.strip() == "":
        st.warning("Please upload a resume and enter the job description before analyzing.")
    else:
        loader_slot.markdown(loader_html(0), unsafe_allow_html=True)
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", resume_file.name)
        with open(file_path, "wb") as f:
            f.write(resume_file.getbuffer())
        time.sleep(0.3)

        resume_text = extract_text(file_path)
        loader_slot.markdown(loader_html(1), unsafe_allow_html=True)
        time.sleep(0.3)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        result = compare_skills(jd_skills, resume_skills)
        loader_slot.markdown(loader_html(2), unsafe_allow_html=True)
        time.sleep(0.3)

        jd_years = extract_experience(jd_text)
        resume_years = extract_experience(resume_text)
        exp_result = compare_experience(jd_years, resume_years)
        loader_slot.markdown(loader_html(3), unsafe_allow_html=True)
        time.sleep(0.3)

        score = result['match_percentage']

        if score >= 75:
            circle_color = "#10b981"
            banner_class = "banner-strong"
            verdict_label = "Strong match"
            verdict_text = "Strong Match — Candidate meets most of the job requirements."
        elif score >= 50:
            circle_color = "#f59e0b"
            banner_class = "banner-moderate"
            verdict_label = "Moderate match"
            verdict_text = "Moderate Match — Candidate meets some requirements, review missing skills."
        else:
            circle_color = "#f43f5e"
            banner_class = "banner-weak"
            verdict_label = "Weak match"
            verdict_text = "Weak Match — Candidate is missing many required skills."

        jd_list_str = ", ".join([s.title() for s in jd_skills]) if jd_skills else "no specific skills"
        resume_list_str = ", ".join([s.title() for s in resume_skills]) if resume_skills else "no specific skills"
        matching_str = ", ".join([s.title() for s in result['matching_skills']]) if result['matching_skills'] else "none"
        missing_str = ", ".join([s.title() for s in result['missing_skills']]) if result['missing_skills'] else "none"

        report_text = f"""SMART RESUME MATCHER - COMPATIBILITY REPORT
Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}

Overall Match Score: {score}%
Verdict: {verdict_text}

Job Description Requires: {jd_list_str}
Resume Contains: {resume_list_str}

Matching Skills: {matching_str}
Missing Skills (Required but not found): {missing_str}
Additional Skills (Not required, but present): {', '.join(result['extra_skills']) if result['extra_skills'] else 'None'}

Experience Check: {exp_result['message']}
"""

        # Persist results so theme toggles / downloads don't wipe the report
        st.session_state["analysis"] = {
            "resume_name": resume_file.name,
            "generated": datetime.now().strftime('%d %b %Y, %H:%M'),
            "file_stamp": datetime.now().strftime('%Y%m%d_%H%M'),
            "resume_skills": resume_skills, "jd_skills": jd_skills, "result": result,
            "jd_years": jd_years, "resume_years": resume_years, "exp_result": exp_result,
            "score": score, "circle_color": circle_color, "banner_class": banner_class,
            "verdict_label": verdict_label, "verdict_text": verdict_text,
            "jd_list_str": jd_list_str, "resume_list_str": resume_list_str,
            "matching_str": matching_str, "missing_str": missing_str, "report_text": report_text,
        }
        loader_slot.empty()

analysis = st.session_state.get("analysis")

# ---------------- Empty state ----------------
if analysis is None:
    resume_ok = resume_file is not None
    jd_ok = jd_text.strip() != ""
    r_cls, r_ic = ("ok", icon("check-circle", 16)) if resume_ok else ("wait", icon("circle", 16))
    j_cls, j_ic = ("ok", icon("check-circle", 16)) if jd_ok else ("wait", icon("circle", 16))
    render(f"""
    <div class="empty">
        <div class="empty-icon">{icon("file-text", 34)}</div>
        <p class="empty-title">No analysis yet</p>
        <p class="empty-sub">Upload a resume and paste a job description above, then run the analysis to see your compatibility report.</p>
        <div class="checklist">
            <span class="check {r_cls}">{r_ic}Resume {"uploaded" if resume_ok else "required"}</span>
            <span class="check {j_cls}">{j_ic}Job description {"added" if jd_ok else "required"}</span>
        </div>
        <div class="feature-grid">
            <div class="feature">
                <div class="metric-icon tone-info">{icon("target", 20)}</div>
                <p class="feature-title">Match score</p>
                <p class="feature-text">An at-a-glance percentage showing how well the resume fits the role.</p>
            </div>
            <div class="feature">
                <div class="metric-icon tone-good">{icon("layers", 20)}</div>
                <p class="feature-title">Skill gap analysis</p>
                <p class="feature-text">Matched, missing and additional skills, clearly separated.</p>
            </div>
            <div class="feature">
                <div class="metric-icon tone-warn">{icon("clock", 20)}</div>
                <p class="feature-title">Experience check</p>
                <p class="feature-text">Compares required years of experience with the candidate's.</p>
            </div>
        </div>
    </div>
    """)

# ---------------- Results ----------------
else:
    a = analysis
    result = a["result"]
    jd_skills = a["jd_skills"]
    resume_skills = a["resume_skills"]
    exp_result = a["exp_result"]
    jd_years = a["jd_years"]
    resume_years = a["resume_years"]
    score = a["score"]
    circle_color = a["circle_color"]
    banner_class = a["banner_class"]
    verdict_text = a["verdict_text"]

    n_match = len(result["matching_skills"])
    n_missing = len(result["missing_skills"])
    n_extra = len(result["extra_skills"])
    n_req = len(jd_skills)

    jd_n = _num(jd_years)
    res_n = _num(resume_years)

    if exp_result["status"] == "meets_requirement":
        exp_tone, exp_banner, exp_sub = "good", "banner-strong", "Meets requirement"
    elif exp_result["status"] == "below_requirement":
        exp_tone, exp_banner, exp_sub = "bad", "banner-weak", "Below requirement"
    else:
        exp_tone, exp_banner, exp_sub = "info", "banner-info", "Not conclusive"

    score_tone = "good" if score >= 75 else ("warn" if score >= 50 else "bad")
    exp_value = f"{_fmt(res_n)} yrs" if res_n is not None else "N/A"

    render(f"""
    <div class="result-head">
        <div>
            <p class="result-title">Compatibility Report</p>
            <p class="result-sub">Resume: {a["resume_name"]} &nbsp;•&nbsp; Generated {a["generated"]}</p>
        </div>
        <span class="nav-pill">{icon("check-circle", 14)}Analysis complete</span>
    </div>
    """)

    # ---- Metric cards ----
    render(f"""
    <div class="metric-grid">
        {metric_card("target", "Match Score", f"{score}%", a["verdict_label"], score_tone)}
        {metric_card("check-circle", "Matched Skills", n_match, f"of {n_req} required", "good")}
        {metric_card("alert-circle", "Missing Skills", n_missing, "required, not found", "bad" if n_missing else "neutral")}
        {metric_card("briefcase", "Experience", exp_value, exp_sub, exp_tone)}
    </div>
    """)

    tab_overview, tab_skills, tab_insights = st.tabs(["Overview", "Skill Breakdown", "Insights"])

    # ================= Overview =================
    with tab_overview:
        left, right = st.columns([1, 1.7], gap="medium")

        with left:
            with st.container(border=True):
                section_title("target", "Step 2: Compatibility Overview", "Overall fit for this role")
                st.markdown(score_ring(score, circle_color), unsafe_allow_html=True)
                st.markdown(f'<div class="{banner_class}">{verdict_text}</div>', unsafe_allow_html=True)

        with right:
            with st.container(border=True):
                section_title("trending-up", "Coverage Analytics", "How the resume lines up with the job")

                total = n_match + n_missing + n_extra
                if total > 0:
                    w_m, w_x, w_e = n_match / total * 100, n_missing / total * 100, n_extra / total * 100
                else:
                    w_m = w_x = w_e = 0
                match_pct = round(n_match / n_req * 100) if n_req else 0

                bars = f"""
                <div class="bar-row">
                    <div class="bar-top"><p class="bar-name">Required skills matched</p><p class="bar-val">{n_match} / {n_req} &nbsp;({match_pct}%)</p></div>
                    <div class="progress"><div class="progress-fill" style="width:{match_pct}%;background:{circle_color}"></div></div>
                </div>
                <div class="bar-row">
                    <div class="bar-top"><p class="bar-name">Skill distribution</p><p class="bar-val">{total} total</p></div>
                    <div class="stack">
                        <div style="width:{w_m:.1f}%;background:#10b981"></div>
                        <div style="width:{w_x:.1f}%;background:#f43f5e"></div>
                        <div style="width:{w_e:.1f}%;background:#94a3b8"></div>
                    </div>
                    <div class="legend">
                        <span><i style="background:#10b981"></i>Matched ({n_match})</span>
                        <span><i style="background:#f43f5e"></i>Missing ({n_missing})</span>
                        <span><i style="background:#94a3b8"></i>Additional ({n_extra})</span>
                    </div>
                </div>
                """
                if jd_n is not None and res_n is not None:
                    mx = max(jd_n, res_n, 1)
                    cand_color = "#10b981" if exp_tone == "good" else ("#f43f5e" if exp_tone == "bad" else "#6366f1")
                    bars += f"""
                    <div class="bar-row">
                        <div class="bar-top"><p class="bar-name">Required experience</p><p class="bar-val">{_fmt(jd_n)} yrs</p></div>
                        <div class="progress"><div class="progress-fill" style="width:{jd_n / mx * 100:.1f}%;background:#6366f1"></div></div>
                    </div>
                    <div class="bar-row">
                        <div class="bar-top"><p class="bar-name">Candidate experience</p><p class="bar-val">{_fmt(res_n)} yrs</p></div>
                        <div class="progress"><div class="progress-fill" style="width:{res_n / mx * 100:.1f}%;background:{cand_color}"></div></div>
                    </div>
                    """
                st.markdown(_h(bars), unsafe_allow_html=True)

                section_title("clock", "Experience Check")
                st.markdown(f'<div class="{exp_banner}" style="margin-top:0;">{exp_result["message"]}</div>', unsafe_allow_html=True)

    # ================= Skill breakdown =================
    with tab_skills:
        with st.container(border=True):
            section_title("layers", "Skill Breakdown", "Matched, missing and additional skills")
            c1, c2, c3 = st.columns(3, gap="large")

            with c1:
                st.markdown(f'<p class="sub-heading"><span>Matching Skills</span><span class="count-pill">{n_match}</span></p>', unsafe_allow_html=True)
                if result["matching_skills"]:
                    badges = "".join([f'<span class="badge-match">{s}</span>' for s in result["matching_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.markdown('<p class="body-text">No matching skills found.</p>', unsafe_allow_html=True)

            with c2:
                st.markdown(f'<p class="sub-heading"><span>Missing Skills (Required but not found)</span><span class="count-pill">{n_missing}</span></p>', unsafe_allow_html=True)
                if result["missing_skills"]:
                    badges = "".join([f'<span class="badge-missing">{s}</span>' for s in result["missing_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.markdown('<p class="body-text">No missing skills — great match!</p>', unsafe_allow_html=True)

            with c3:
                st.markdown(f'<p class="sub-heading"><span>Additional Skills (Not required, but present)</span><span class="count-pill">{n_extra}</span></p>', unsafe_allow_html=True)
                if result["extra_skills"]:
                    badges = "".join([f'<span class="badge-extra">{s}</span>' for s in result["extra_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.markdown('<p class="body-text">No extra skills.</p>', unsafe_allow_html=True)

        if jd_skills:
            with st.container(border=True):
                section_title("check-circle", "Requirement Checklist", "Every skill required by the job description")
                rows = ""
                for s in jd_skills:
                    if s in result["matching_skills"]:
                        pill = f'<span class="pill pill-good">{icon("check-circle", 13)}Matched</span>'
                    else:
                        pill = f'<span class="pill pill-bad">{icon("alert-circle", 13)}Not found</span>'
                    rows += f'<div class="req-row"><p class="req-name">{s.title()}</p>{pill}</div>'
                st.markdown(_h(rows), unsafe_allow_html=True)

    # ================= Insights =================
    with tab_insights:
        with st.container(border=True):
            section_title("file-text", "Compatibility Explanation", "A plain-language summary of the result")

            explanation = f"""
            The job description requires the following skills: <b>{a["jd_list_str"]}</b>.<br><br>
            The candidate's resume contains: <b>{a["resume_list_str"]}</b>.<br><br>
            Comparing the two, the candidate <b>matches {n_match} out of {n_req} required skills</b>:
            <b>{a["matching_str"]}</b>.<br><br>
            The following required skills are <b>not clearly present in the resume</b>: <b>{a["missing_str"]}</b>.
            """
            st.markdown(f'<div class="explanation-box">{_h(explanation)}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            section_title("lightbulb", "Recommendations", "Suggested next steps")

            if result["missing_skills"]:
                rec_items = "".join([f"<li>{s.title()}</li>" for s in result["missing_skills"]])
                recommendation_html = f"""
                To improve the match score, the candidate should consider gaining or highlighting experience in:
                <ul>{rec_items}</ul>
                """
            else:
                recommendation_html = "The candidate covers all required skills for this role. No gaps identified."

            if exp_result["status"] == "below_requirement":
                recommendation_html += f"<br>Consider candidates with experience closer to the required <b>{jd_years}+ years</b>, or verify if project experience compensates for fewer years."

            st.markdown(f'<div class="recommend-box">{_h(recommendation_html)}</div>', unsafe_allow_html=True)

    # ---- Downloadable Report ----
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download Full Report (.txt)",
        data=a["report_text"],
        file_name=f"resume_report_{a['file_stamp']}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ---------------- Footer ----------------
render('<div class="footer">Smart Resume Matcher © 2026 | Internal Recruitment Tool</div>')