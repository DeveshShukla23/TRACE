<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:0A0A0A,40:0A0A0A,70:FF0000,100:FF6600&height=230&section=header&text=TRACE&fontSize=80&fontColor=E8E8E8&fontAlignY=38&desc=Trend%20Recognition%20and%20Automated%20Cause%20Explanation%20%7C%20AI%20Root%20Cause%20Analyzer&descAlignY=62&descSize=14&descColor=C0C0C0&animation=fadeIn)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&pause=1000&color=FF0000&center=true&vCenter=true&width=960&lines=Upload+Any+Business+CSV+%2F+Excel+%E2%86%92+Instant+Root+Cause+Analysis;9+Anomaly+Detection+Methods+%7C+Z-Score+%7C+IQR+%7C+Isolation+Forest;Correlation+Engine+%7C+Lag+Detection+%7C+Pareto+Ranking;LLaMA+3.3+70B+Narrated+Reports+%7C+Groq+API+%7C+Zero+Manual+Work)](https://git.io/typing-svg)

<br>

![Python](https://img.shields.io/badge/Python-0A0A0A?style=for-the-badge&logo=python&logoColor=FF0000)
![Streamlit](https://img.shields.io/badge/Streamlit-0A0A0A?style=for-the-badge&logo=streamlit&logoColor=FF0000)
![Groq](https://img.shields.io/badge/Groq_LLaMA_3.3_70B-0A0A0A?style=for-the-badge&logo=meta&logoColor=FF6600)
![Pandas](https://img.shields.io/badge/Pandas-0A0A0A?style=for-the-badge&logo=pandas&logoColor=E8E8E8)
![NumPy](https://img.shields.io/badge/NumPy-0A0A0A?style=for-the-badge&logo=numpy&logoColor=E8E8E8)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-0A0A0A?style=for-the-badge&logo=scikit-learn&logoColor=FF6600)
![Plotly](https://img.shields.io/badge/Plotly-0A0A0A?style=for-the-badge&logo=plotly&logoColor=E8E8E8)
![SciPy](https://img.shields.io/badge/SciPy-0A0A0A?style=for-the-badge&logo=scipy&logoColor=E8E8E8)

<br>

[![Live App](https://img.shields.io/badge/Live-trace--analyzer.streamlit.app-FF0000?style=for-the-badge&logo=streamlit&logoColor=white)](https://trace-analyzer.streamlit.app)
![Detection Methods](https://img.shields.io/badge/Detection_Methods-9-FF6600?style=for-the-badge&labelColor=0A0A0A)
![LLM](https://img.shields.io/badge/LLM-LLaMA_3.3_70B-FFD700?style=for-the-badge&labelColor=0A0A0A)
![Domains](https://img.shields.io/badge/Domains-Any_Business_CSV-E8E8E8?style=for-the-badge&labelColor=0A0A0A)
![Report Time](https://img.shields.io/badge/Analysis_Time-Under_2_Min-00CC44?style=for-the-badge&labelColor=0A0A0A)

<br>

[![GitHub](https://img.shields.io/badge/GitHub-DeveshShukla23-0A0A0A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DeveshShukla23)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Devesh%20Shukla-FF0000?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/devesh-shukla23)
[![Email](https://img.shields.io/badge/Email-Contact-FF6600?style=for-the-badge&logo=gmail&logoColor=white)](mailto:shukladevesh40@gmail.com)

</div>

---

<div align="center">

**The diagnostic color system that powers TRACE**

![#FF0000](https://img.shields.io/badge/%20-%20-FF0000?style=flat-square) `#FF0000 — CRITICAL`
&nbsp;&nbsp;&nbsp;
![#FF6600](https://img.shields.io/badge/%20-%20-FF6600?style=flat-square) `#FF6600 — HIGH`
&nbsp;&nbsp;&nbsp;
![#FFD700](https://img.shields.io/badge/%20-%20-FFD700?style=flat-square) `#FFD700 — MEDIUM`
&nbsp;&nbsp;&nbsp;
![#00CC44](https://img.shields.io/badge/%20-%20-00CC44?style=flat-square) `#00CC44 — NORMAL`

</div>

---

## 🤔 Why was TRACE built?

When something breaks in a business — revenue drops, returns spike, a KPI goes red — the standard process is painful:

1. Someone notices the problem (often days late)
2. An analyst manually digs through spreadsheets
3. They run correlations, check time periods, compare columns
4. They write a report explaining what happened and why
5. That report reaches a decision-maker — **2 to 3 days later**

**That delay is the problem TRACE was built to eliminate.**

Most small and mid-size teams don't have a dedicated data analyst available on demand. And even when they do, manual root cause analysis is slow, inconsistent, and often misses patterns that span multiple columns simultaneously.

> 💡 *"The business already has the data. The problem is it takes too long to hear what the data is trying to say. TRACE makes that conversation instant."*

---

## 🧠 What is TRACE?

**TRACE — Trend Recognition and Automated Cause Explanation** is an AI-powered root cause analyzer built on Streamlit.

You upload any business CSV or Excel file. TRACE automatically:
- Detects statistical anomalies across every numeric column
- Finds correlations and root causes between columns
- Generates an AI-narrated diagnostic report in plain English

**No configuration. No coding. No manual analysis.**

It works on any business domain — sales, HR, logistics, finance, operations, e-commerce — as long as your data has numeric columns and dates.

---

## ⚙️ What does TRACE actually do?

<div align="center">

| Stage | What Happens | Output |
|:---:|---|---|
| **01 — Load** | Cleans file, detects 13 data quality issue types, identifies metric vs dimension columns | Data Quality Report |
| **02 — Detect** | Runs 9 anomaly detection methods on every numeric column | Anomaly DataFrame with severity tags |
| **03 — Correlate** | Finds what moved with what — contribution %, lag effects, Pareto ranking | Correlation Summary per column |
| **04 — Narrate** | Sends top 5 critical columns to LLaMA 3.3 70B — generates plain English root cause reports | AI Report per column |
| **05 — Display** | Renders KPI cards, Plotly charts, heatmap, timeline, driver evidence cards | Full diagnostic dashboard |

</div>

---

## 🔍 How does TRACE detect anomalies?

TRACE runs **9 independent detection methods** on every numeric column simultaneously:

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    TRACE — 9 DETECTION METHODS                          ║
╠══════════════════╦══════════════════════════════════════════════════════╣
║  Method          ║  What It Catches                                     ║
╠══════════════════╬══════════════════════════════════════════════════════╣
║  Z-Score         ║  Global statistical outliers (> 3σ from mean)       ║
║  Modified Z      ║  Outliers robust to non-normal distributions        ║
║  Rolling Z-Score ║  Local outliers within a moving time window         ║
║  IQR             ║  Business anomalies using 1.5× interquartile range  ║
║  Rate of Change  ║  Sudden spikes or drops between consecutive rows    ║
║  Isolation Forest║  ML-based multi-dimensional anomaly detection       ║
║  Cross-Column    ║  Divergence between columns that normally move together ║
║  Zero Detection  ║  Unexpected zero values in non-zero metric columns  ║
║  Volume Detection║  Unusual data volume patterns across time periods   ║
║  Level Shift     ║  Permanent structural changes in baseline behavior  ║
╚══════════════════╩══════════════════════════════════════════════════════╝
```

**Why 9 methods?** A single method will miss patterns another catches. When multiple methods agree on the same data point, TRACE marks it `[ VERIFIED ]` — high confidence it's a real anomaly, not noise.

---

## 🔗 How does the Correlation Engine work?

Detecting an anomaly is only half the job. The harder question is: **why did it happen?**

TRACE's correlation engine answers this by:

- **Contribution %** — which dimension (region, product, category) is responsible for what share of the anomaly
- **Lagged Correlation** — did Column B spike 2 weeks *before* Column A crashed? Lag detection finds cause-and-effect across time
- **Spurious Detection** — filters out coincidental correlations that have no real business relationship
- **Pareto Ranking** — surfaces the top drivers by impact, not just by correlation coefficient
- **Multi-Dimension Interaction** — finds combinations of dimensions that together explain the anomaly

---

## 🤖 How does AI narration work?

After detection and correlation, TRACE has a complete statistical picture of each anomaly. It sends that evidence to **Groq LLaMA 3.3 70B** with a structured prompt and gets back a plain English root cause report.

**What goes into the prompt:**
- Severity breakdown (how many critical, high, medium anomalies)
- Trend direction (worsening, recovering, stable)
- Primary dimension driver (which category caused most of the problem)
- Primary metric driver (which other column moved with it)
- Lag information (was there a delayed effect)
- Statistical confidence level

**What comes out:**
A human-readable diagnostic paragraph that a non-technical stakeholder can read and act on immediately.

> ⚠️ **AI Disclaimer:** Every report generated by TRACE includes an explicit AI disclaimer. TRACE identifies patterns and proposes explanations — final business decisions remain with the analyst or decision-maker.

---

## 🚨 How to read TRACE output

<div align="center">

| Signal | What It Means | What To Do |
|:---:|---|---|
| 🔴 **CRITICAL** | Severely outside normal range — immediate attention needed | Investigate now |
| 🟠 **HIGH** | Significant deviation — investigate soon | Review within 24–48h |
| 🟡 **MEDIUM** | Minor anomaly — monitor | Track over next period |
| 🟢 **NORMAL** | Within expected statistical range | No action needed |
| `[ VERIFIED ]` | 3+ detection methods agreed — real anomaly, high confidence | Trust this signal |
| `[ CONFIRMED ]` | 2 methods agreed | Likely real |
| `[ PROBABLE ]` | 1 method flagged — could be noise | Investigate with context |
| `[ UNCERTAIN ]` | Borderline — very low confidence | Monitor only |

</div>

**Reading a column report — in order:**

1. **Severity badge** — how serious is the problem overall
2. **Confidence badge** — how many methods agreed
3. **Trend direction** — is it getting worse or recovering
4. **Anomaly chart** — red dots show exactly *when* anomalies occurred on the timeline
5. **Dimension Driver card** — *which category* is responsible and what % contribution
6. **Metric Driver card** — *which other column* moved with this anomaly and by how much
7. **AI Report** — plain English explanation of what happened and why

---

## 💥 What problem does TRACE solve?

<div align="center">

| Without TRACE | With TRACE |
|---|---|
| Manual anomaly detection — days of work | Automatic detection across all columns — seconds |
| One analyst, one method, one perspective | 9 methods running simultaneously |
| Root cause found by intuition | Root cause found by statistical evidence |
| Report written manually — inconsistent quality | AI-narrated report — consistent, structured |
| Only the columns someone thought to check | Every numeric column checked automatically |
| Requires a skilled data analyst on demand | Any business user can upload and read results |
| 2–3 days from problem to explanation | Under 2 minutes from upload to full report |

</div>

---

## 📊 Concrete Example — BMW Sales Data

> Upload `BMW_Sales_Raw.csv` (4,569 rows, 29 columns) → TRACE runs in under 90 seconds

**What TRACE finds automatically:**

```
SYSTEM HEALTH  →  CRITICAL
CRITICAL       →  5,555 anomalies
HIGH           →  276 anomalies
MEDIUM         →  48 anomalies
```

**Example column report — Revenue:**
- Severity: `CRITICAL` | Confidence: `[ VERIFIED ]` | Trend: `DECLINING`
- Dimension Driver: `REGION = USA — 67% contribution — STRONG signal`
- Metric Driver: `DISCOUNT_RATE — up 42% during anomaly period — 2 row lag detected`

**AI Report output:**
> *"Revenue experienced critical anomalies concentrated in Q3, driven primarily by the USA region which contributed 67% of the total deviation. Analysis reveals a 42% spike in Discount_Rate with a 2-period lead, suggesting aggressive discounting attracted high-return or low-margin customers. Sustained anomaly groups indicate a structural issue rather than a one-time event — a targeted USA pricing policy review is recommended."*

**Time taken:** 90 seconds. Manual equivalent: 2–3 days.

---

## 🎯 What impact does TRACE create?

```
⚡  Detection Speed    →  Days of manual work compressed to under 2 minutes
🔍  Coverage          →  Every numeric column checked — nothing missed by assumption
🧠  Depth             →  9 methods + correlation + lag + AI narration in one pass
📋  Consistency       →  Same structured report quality every time — no analyst variability
👥  Accessibility     →  Non-technical users can read and act on results without analyst help
🌐  Domain Agnostic   →  Sales, HR, logistics, finance, operations — any business CSV works
💰  Cost              →  Replaces hours of analyst time per investigation
```

---

## 🏗️ System Architecture

```
╔═══════════════════════════════════════════════════════════════════╗
║                    TRACE — SYSTEM PIPELINE                        ║
╠══════════════╦════════════════════════════╦══════════════════════╣
║  Module      ║  Responsibility            ║  Key Methods         ║
╠══════════════╬════════════════════════════╬══════════════════════╣
║  loader.py   ║  File ingestion & cleaning ║  3.5× IQR error det  ║
║  detector.py ║  9-method anomaly scan     ║  1.5× IQR + ML       ║
║  correlator.py ║ Root cause tracing       ║  Lag + Pareto        ║
║  narrator.py ║  LLM report generation     ║  Groq LLaMA 3.3 70B  ║
║  helpers.py  ║  Utility functions         ║  Severity scoring    ║
║  theme.py    ║  Full UI dark theme        ║  CSS injection       ║
║  app.py      ║  Streamlit orchestration   ║  Full pipeline ctrl  ║
╚══════════════╩════════════════════════════╩══════════════════════╝
```

---

## 📂 Project Structure

```
TRACE/
│
├── 📄 app.py                    # Main Streamlit app — full pipeline orchestration
│
├── 📁 engine/
│   ├── __init__.py              # Package init
│   ├── loader.py                # File ingestion, data cleaning, column detection
│   ├── detector.py              # 9-method anomaly detection engine
│   ├── correlator.py            # Correlation, lag, Pareto, driver analysis
│   └── narrator.py              # Groq LLaMA 3.3 70B report generation
│
├── 📁 utils/
│   ├── __init__.py              # Package init
│   ├── helpers.py               # Severity scoring, formatting, badge utilities
│   └── theme.py                 # Full custom dark theme CSS injection
│
├── 📄 .env                      # GROQ_API_KEY (never commit to GitHub)
└── 📄 requirements.txt          # All dependencies
```

---

## 🛠️ Tech Stack

```
Core App      →  Python 3.x + Streamlit
Data Layer    →  Pandas + NumPy
Statistics    →  SciPy (Z-score, IQR, correlation)
ML Detection  →  Scikit-learn (Isolation Forest)
Fuzzy Match   →  RapidFuzz (column name intelligence)
Visualization →  Plotly (dark theme charts + heatmaps)
AI Narration  →  Groq API — LLaMA 3.3 70B
Config        →  python-dotenv
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/DeveshShukla23/TRACE.git
cd TRACE

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
# Create a .env file in the root directory
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Run TRACE
streamlit run app.py
```

Get your free Groq API key at: [console.groq.com](https://console.groq.com)

---

## 📋 Requirements

```
streamlit
pandas
numpy
scipy
scikit-learn
plotly
groq
rapidfuzz
python-dotenv
openpyxl
```

---

<div align="center">

## 👨‍💻 Author

**Devesh Shukla**
*Data Analyst · AI / GenAI Developer · Python · SQL · Power BI · Machine Learning*

*Fresher with hands-on project experience across end-to-end data pipelines,*
*ML models, and production-grade GenAI applications*

<br>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-FF0000?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/devesh-shukla23)
[![GitHub](https://img.shields.io/badge/GitHub-DeveshShukla23-0A0A0A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DeveshShukla23)
[![Email](https://img.shields.io/badge/Email-Reach_Me-FF6600?style=for-the-badge&logo=gmail&logoColor=white)](mailto:shukladevesh40@gmail.com)

<br>

*"Most tools show you what happened.*
*TRACE tells you why."*

<br>

⭐ **If TRACE saved you time, give it a star!** ⭐

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:FF6600,40:FF0000,70:0A0A0A,100:0A0A0A&height=130&section=footer&animation=fadeIn)

</div>
