# ARR Performance & Retention Intelligence

A lightweight, fully local BI dashboard prototype for monitoring recurring revenue growth, contraction, and churn risk. Built as a portfolio project to demonstrate the full analytics pipeline: **raw data → data preparation → KPI definition → BI dashboard → business insight → AI-style narrative layer.**

> **Note:** Underlying figures are real business data that has been anonymized and aggregated for demonstration. Team names have been replaced with neutral region labels (Region A–D). No customer-identifiable information is displayed.

## Purpose

Answer three business questions for management / sales / customer success stakeholders:

1. **Executive Overview** — How is ARR performing overall?
2. **Team Performance** — Which regions drive growth vs. create ARR risk?
3. **Retention & Churn** — Where are we losing ARR, and how concentrated is that risk?

## Tech Stack

```
Excel (raw data)
   ↓
Python / Pandas   → cleaning, KPI calculation, anonymization
   ↓
CSV (local data layer, no database)
   ↓
Streamlit + Plotly → interactive BI dashboard
   ↓
Rule-based insight engine → AI-style business narrative (V1, no external API)
```

Deliberately **no** database, cloud service, Power BI/Tableau license, backend API, or authentication layer — this is a local analytics prototype designed to be run and demoed in minutes, not a production system.

## Data Dictionary

| Field | Definition |
|---|---|
| Expansion ARR | Recurring revenue increase from existing customers upgrading/adding seats |
| Contraction ARR | Recurring revenue decrease from existing customers downgrading (stored as negative) |
| Lost ARR | Recurring revenue lost from customers who fully churned (stored as positive) |
| Net ARR Movement | Expansion ARR + Contraction ARR − Lost ARR |
| Avg ARR Lost / Customer | Lost ARR ÷ Lost Customer Count — proxy for whether churn is concentrated in high-value accounts |
| Concentration Gap | (% of Lost ARR) − (% of Lost Customers) per region. Positive = loss concentrated in fewer, higher-value accounts |

## Data Coverage & Assumptions

- **2024 Team-level data (Region A–D):** actual for Jan–Apr 2024 only. No May–Dec figures exist in the source, and none were fabricated.
- **Yearly Overview (Renewed/Churned ARR):** full year for 2022 and 2023; Jan–Apr only for 2024.
- Team → Region anonymization mapping: China → Region A, Portugal → Region B, Scalemill → Region C, Turkey → Region D.

## Key Insight Surfaced in V1

In January 2024, Region C (anonymized) accounted for ~60% of total Lost ARR (€70,700 of €117,100) while also representing ~60% of lost customers — meaning the loss was **broad-based rather than concentrated in a few high-value accounts**. This is a more nuanced finding than "a few big customers churned," and is a good talking point for interviews about how BI moves from reporting to analysis.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Ensure `team_arr_2024.csv` and `yearly_overview.csv` are in the same folder as `app.py`.

## Roadmap (for interview storytelling)

- **V1 (this version):** Excel → Pandas → Streamlit BI dashboard with rule-based insight generation.
- **V2:** Deeper analytics — expansion/contraction rates, growth vs. churn contribution scoring, customer-level risk segmentation (requires customer-level data, not currently available).
- **V3:** Swap the rule-based insight engine for an LLM-backed "Ask the Dashboard" feature and an auto-generated executive summary.

## Suggested Interview Framing

- BI layer → tells us **what** happened.
- Analytics layer → tells us **where** and **how significant**.
- AI layer (roadmap) → helps explain **what it means** and **what to investigate next**.

If asked *"why no database?"*: *"This was designed as a lightweight analytics prototype rather than a production BI system, to demonstrate how I transform raw business data into an interactive decision-support dashboard. For production, I'd move the data layer to a governed database or warehouse."*
