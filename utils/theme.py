def inject_theme():
    import streamlit as st

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* ── ROOT RESET ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], .main, .block-container {
        background-color: #0A0A0A !important;
        color: #E8E8E8 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── HIDE STREAMLIT DEFAULTS ── */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background-color: #0D0D0D !important;
        border-right: 1px solid #1E1E1E !important;
    }
    [data-testid="stSidebar"] * {
        color: #E8E8E8 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── BLOCK CONTAINER PADDING ── */
    .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1400px !important;
    }

    /* ── HEADINGS ── */
    h1, h2, h3, h4, h5, h6 {
        color: #E8E8E8 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
    }

    /* ── PARAGRAPHS AND LABELS ── */
    /* NOTE: Intentionally NOT setting font-family here to avoid
       overriding Material Icons font used by Streamlit icon spans */
    p, label {
        color: #E8E8E8 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── METRIC CARDS ── */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 6px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #666666 !important;
        font-size: 11px !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    [data-testid="stMetricValue"] {
        color: #E8E8E8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background-color: #111111 !important;
        border: 1px dashed #333333 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #555555 !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background-color: #1A1A1A !important;
        color: #E8E8E8 !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #222222 !important;
        border-color: #555555 !important;
        color: #FFFFFF !important;
    }

    /* ── SELECTBOX AND INPUTS ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: #111111 !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 4px !important;
        color: #E8E8E8 !important;
    }

    /* ── DATAFRAME / TABLES ── */
    [data-testid="stDataFrame"] {
        background-color: #111111 !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 6px !important;
    }
    .stDataFrame th {
        background-color: #161616 !important;
        color: #666666 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid #1E1E1E !important;
    }
    .stDataFrame td {
        background-color: #111111 !important;
        color: #E8E8E8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        border-bottom: 1px solid #161616 !important;
    }

    /* ── EXPANDER — FULL FIX ── */
    [data-testid="stExpander"] {
        background-color: #111111 !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 4px !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] > details > summary,
    .streamlit-expanderHeader {
        background-color: #111111 !important;
        border-radius: 4px !important;
        color: #E8E8E8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.5px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0.75rem 1rem !important;
        list-style: none !important;
        cursor: pointer !important;
        min-height: 44px !important;
    }

    [data-testid="stExpander"] summary::-webkit-details-marker,
    [data-testid="stExpander"] > details > summary::-webkit-details-marker {
        display: none !important;
    }

    [data-testid="stExpander"] summary::marker,
    [data-testid="stExpander"] > details > summary::marker {
        display: none !important;
    }

    /* ── EXPANDER ICON FIX ──
       Root cause: the blanket "p, span, label, div" rule was overriding
       Material Icons font with Inter, breaking the icon ligature into raw text.
       Fix: hide the icon span entirely. The expander title text is self-explanatory.
    ── */
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary span[aria-hidden="true"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        font-size: 0 !important;
    }

    .streamlit-expanderHeader p,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] > details > summary p,
    [data-testid="stExpander"] > details > summary span {
        margin: 0 !important;
        padding: 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        color: #E8E8E8 !important;
        position: static !important;
        display: inline !important;
    }

    /* Re-hide any span that still sneaks through as raw icon text */
    [data-testid="stExpander"] summary span:empty,
    [data-testid="stExpander"] summary span[class*="material"],
    [data-testid="stExpander"] summary span[class*="icon"] {
        display: none !important;
    }

    .streamlit-expanderContent,
    [data-testid="stExpander"] > details > div,
    [data-testid="stExpanderDetails"] {
        background-color: #0D0D0D !important;
        border-top: 1px solid #1E1E1E !important;
        padding: 1rem !important;
    }

    /* ── DIVIDER ── */
    hr {
        border-color: #1E1E1E !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 4px !important; height: 4px !important; }
    ::-webkit-scrollbar-track { background: #0A0A0A !important; }
    ::-webkit-scrollbar-thumb { background: #333333 !important; border-radius: 2px !important; }

    /* ── PLOTLY CHART BACKGROUND ── */
    .js-plotly-plot .plotly { background-color: #0A0A0A !important; }

    /* ── PROGRESS BAR ── */
    .stProgress > div > div { background-color: #C0C0C0 !important; }

    /* ── ALERTS ── */
    .stAlert {
        background-color: #111111 !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 4px !important;
        color: #E8E8E8 !important;
    }

    /* ── SEVERITY PULSE ANIMATION ── */
    @keyframes pulse-red {
        0%   { text-shadow: 0 0 4px #FF000088; opacity: 1; }
        50%  { text-shadow: 0 0 16px #FF0000CC; opacity: 0.7; }
        100% { text-shadow: 0 0 4px #FF000088; opacity: 1; }
    }

    @keyframes pulse-glow-border {
        0%   { box-shadow: 0 0 4px #FF000044; border-color: #FF0000; }
        50%  { box-shadow: 0 0 16px #FF000088; border-color: #FF4444; }
        100% { box-shadow: 0 0 4px #FF000044; border-color: #FF0000; }
    }

    /* ── TRACE CUSTOM CARDS ── */
    .trace-card {
        background-color: #111111;
        border: 1px solid #1E1E1E;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .trace-card-critical {
        background-color: #110000;
        border: 1px solid #FF0000;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        animation: pulse-glow-border 1.5s infinite;
    }

    .trace-card-high {
        background-color: #111111;
        border: 1px solid #FF6600;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .trace-card-medium {
        background-color: #111111;
        border: 1px solid #FFD700;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    /* ── TRACE TYPOGRAPHY ── */
    .trace-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #666666;
        margin-bottom: 4px;
    }

    .trace-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: #E8E8E8;
    }

    .trace-subvalue {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #666666;
        margin-top: 2px;
    }

    .trace-section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #444444;
        border-bottom: 1px solid #1E1E1E;
        padding-bottom: 6px;
        margin-bottom: 1rem;
    }

    .trace-report-box {
        background-color: #0D0D0D;
        border: 1px solid #1E1E1E;
        border-radius: 4px;
        padding: 1.25rem;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        line-height: 1.7;
        color: #CCCCCC;
        white-space: pre-wrap;
    }

    /* ── TRACE SEVERITY BADGES ── */
    .trace-badge-critical {
        color: #FF0000;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        animation: pulse-red 1.2s infinite;
        text-shadow: 0 0 8px #FF000088;
    }

    .trace-badge-high {
        color: #FF6600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .trace-badge-medium {
        color: #FFD700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .trace-badge-normal {
        color: #00CC44;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    /* ── TRACE CONFIDENCE BADGES ── */
    .trace-confidence-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 2px 6px;
        border-radius: 2px;
        border: 1px solid;
    }

    /* ── TRACE HEALTH STATUS ── */
    .trace-health-clean {
        color: #00CC44;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
    }
    .trace-health-moderate {
        color: #FFD700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
    }
    .trace-health-elevated {
        color: #FF6600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
    }
    .trace-health-critical {
        color: #FF0000;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        animation: pulse-red 1.2s infinite;
        text-shadow: 0 0 8px #FF000088;
    }

    </style>
    """, unsafe_allow_html=True)