# HireVue Candidate Score & Insights App

Related: [[Learning Plan - Dev & Data Analyst]] | [[HireVue Interview Prep - Officeworks]] | [[Applied job]]

---

## 1. Overview & Problem Statement

When job candidates complete a HireVue automated interview or assessment (e.g. Officeworks, supermarkets, banks, graduate programs), the candidate portal only displays generic qualitative statements (the "Candidate Insights Report"). 

Candidates never see their actual numbers or understand:
- What their real quantitative scores are across competencies.
- How they performed relative to the pass/fail benchmark.
- What specific behavioral or cognitive areas they need to improve for future job applications.

**The Solution:** A web app where candidates can paste their HireVue interview status link or code to instantly view their raw competency scores (1 to 5 scale), compare them against industry benchmarks, and get an AI-generated improvement action plan.

---

## 2. Technical Findings (Reverse Engineered)

HireVue single-page web applications (`bd-interview-status`) query an unauthenticated GraphQL endpoint on status check:

### Endpoint
* **URL:** `POST https://eu.hirevue.com/ui/graphql` (or `https://hirevue.com/ui/graphql` for US region)
* **Headers:** `Content-Type: application/json`

### GraphQL Query
```graphql
query InterviewStatus($interviewCode: String!) {
  interviewStatus(interviewCode: $interviewCode) {
    companyName
    candidateInsightsReportEnabled
    inlineReturnUrl
    isAvailable
    product
    status
    position {
      interviewType
      isExpired
      title
    }
    assessmentScores {
      id
      score
      scoreType
      error
    }
  }
}
```

### Variables
```json
{
  "interviewCode": "YOUR_INTERVIEW_CODE"
}
```

### Scoring Logic
* **Score Scale:** 1 to 5.
* **HireVue Internal Threshold:** Score > 2.5 is classified as high/strength; score <= 2.5 is classified as low/development area.
* **Competencies Measured:**
  - **Interpersonal & Behavioral:** `team-orientation`, `service-orientation`, `communication`, `negotiation`, `adaptability`, `agreeableness`, `compassion`, `composure`, `conscientiousness`, `dependability`, `drive`, `tenacity`.
  - **Cognitive / Game-based:** `think-agility`, `think-numeracy`, `think-problem-solving`, `think-visuospatial`.

---

## 3. App Features

1. **Score Revealer & Dashboard:**
   - Candidate pastes their link (e.g. `https://eu.hirevue.com/ui/interview-status/#/CODE/`) or enters the code.
   - Extracts the code via regex, queries the API, and renders interactive radar charts or bar charts showing scores out of 5.

2. **Role Fit Analysis:**
   - Evaluates whether the scores are strong for the specific role (e.g. Retail Team Member places highest weight on Team Orientation and Service Orientation; Tech/Analyst roles weight Problem Solving and Numeracy higher).

3. **Improvement Coach & Action Plan:**
   - Highlights development areas (scores <= 2.5).
   - Generates actionable advice and sample behavioral interview answers to improve weak spots in future interviews.

---

## 4. Suggested Tech Stack

* **Backend / Quick MVP:** Python + Streamlit (can be deployed free on Streamlit Cloud, aligning with [[Learning Plan - Dev & Data Analyst]]).
* **Alternative Full-Stack:** FastAPI + SQLite/PostgreSQL + Tailwind/React (or simple clean HTML/JS).
* **AI Integration:** OpenAI / Gemini API to generate personalized improvement recommendations based on the candidate's lowest scores.

---

## 5. Development Roadmap

- [ ] Build standalone Python script to parse interview URLs and fetch JSON payload.
- [ ] Create basic Streamlit UI with input field, radar chart (Plotly), and score cards.
- [ ] Add role-specific benchmark comparisons (Retail, Customer Service, Banking, Graduate).
- [ ] Integrate prompt for AI-generated improvement guidance.
- [ ] Deploy MVP to Streamlit Cloud and link in portfolio.
