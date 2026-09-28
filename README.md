# 🎯 HireVue Candidate Score & Insights App

[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.14-blue.svg)]()
[![Streamlit](https://img.shields.io/badge/streamlit-1.35%2B-red.svg)]()
[![Plotly](https://img.shields.io/badge/plotly-5.20%2B-blueviolet.svg)]()

A data-driven web application that demystifies automated HireVue video and game-based assessments. By querying HireVue's public candidate status GraphQL endpoint, this application extracts hidden quantitative competency scores (1.0 to 5.0), maps candidate performance against industry benchmarks, and generates targeted STAR-method improvement action plans.

---

## 📌 Pain Points Solved: Why Candidates Want This

When candidates finish an automated HireVue interview (common with employers like Officeworks, supermarkets, banks, and graduate programs), the official candidate portal displays generic qualitative statements such as *"You tend to balance teamwork with independent problem solving"*. 

Candidates are left with severe informational blind spots:
1. **The "Black Box" Problem:** Candidates never see their actual mathematical scores across competencies.
2. **Missing Pass/Fail Context:** HireVue internally classifies scores `> 2.5` as strengths and `≤ 2.5` as development areas (risks). Candidates are unaware when a single sub-2.5 competency caused an automatic rejection.
3. **No Actionable Feedback:** Without clear scores, candidates make the same behavioral or cognitive test mistakes across dozens of job applications.

### The Solution
* **Instant Score Reveal:** Paste a HireVue status URL or code to immediately extract raw 1.0–5.0 competency ratings.
* **Role-Fit Radar Charts:** Visually compare personal scores against industry role benchmarks (Retail, Tech/Data Analyst, Banking, Graduate Programs).
* **AI Coaching & STAR Framework:** Automatically detects development areas (≤ 2.5) and generates tailored practice questions, STAR guides, and high-scoring response templates.
* **Instant Demo Mode:** Preloaded with realistic candidate assessment profiles so recruiters and portfolio reviewers can explore the app without needing an active HireVue link.

---

## 🏗️ Architecture & Module Structure

```text
hirevue-insights-app/
├── app.py                      # Streamlit interactive dashboard & visualizations
├── hirevue_client.py           # URL parsing & HireVue GraphQL API client
├── mock_data.py                # Realistic sample candidate assessment profiles
├── benchmarks.py               # Competency taxonomy, threshold logic & role fit engine
├── coach.py                    # STAR-method coaching advice & game strategy generator
├── tests/                      # Comprehensive pytest test suite (21 tests)
│   ├── test_hirevue_client.py
│   ├── test_mock_data.py
│   ├── test_benchmarks.py
│   ├── test_coach.py
│   └── test_app.py
├── requirements.txt            # Project dependencies
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/alate-jane/hirevue-insights-app.git
cd hirevue-insights-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```
The app will launch in your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

The test suite covers URL regex parsing, API response handling, benchmark fit scoring, STAR coaching generation, and Plotly visualization builders:

```bash
pytest tests/ -v
```

Output:
```text
tests/test_app.py::test_create_radar_chart PASSED
tests/test_app.py::test_create_bar_chart PASSED
tests/test_benchmarks.py::test_get_competency_meta_known PASSED
tests/test_benchmarks.py::test_parse_scored_competencies_thresholds PASSED
tests/test_benchmarks.py::test_calculate_role_fit_retail PASSED
tests/test_coach.py::test_generate_coaching_advice_sorting_and_content PASSED
tests/test_hirevue_client.py::test_extract_interview_code_eu_url PASSED
tests/test_mock_data.py::test_get_demo_profile_valid PASSED
============================= 21 passed in 0.15s ==============================
```

---

## 🔒 Privacy & Ethical Note

* This tool only reads public status data for interviews that the candidate is authorized to view.
* No interview codes, candidate identities, or scores are permanently stored or logged in any database.
