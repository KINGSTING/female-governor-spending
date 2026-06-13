# 📊 Do Female Governors Spend More on Health and Public Welfare?
**A Panel Event Study of Philippine Provinces (1992–2022)**

## Overview
This repository contains the data, scripts, and manuscript for a 30-year panel event study examining the causal impact of female local chief executives on provincial resource allocation in the Philippines.

Using a staggered difference-in-differences design, this research investigates whether the election of a female governor shifts public spending toward health and public welfare. The study explicitly addresses biases associated with staggered treatment timing and tests whether observed gender effects operate independently of entrenched political dynastic succession.

This research was conducted as part of the **Policy Hackathon 2026** to bridge computational policy modeling with public administration and governance.

---

## 📌 Key Findings
* **Welfare Spending Increase:** The election of a female governor drives a substantial increase in discretionary public welfare spending—approximately 0.32 log points (roughly a 38% increase) two to three years into their tenure.
* **Dynastic Independence:** This gender-driven fiscal shift persists independently of dynastic succession. Female governors from established political families and non-dynastic female governors both significantly increase welfare spending compared to their male predecessors.
* **Health Spending Rigidities:** While female governors appear to alter health expenditures, significant negative pre-trends were detected. This violates the parallel trends assumption, suggesting provinces electing female governors were already actively reducing health spending prior to the executive transition.
* **Policy Implications:** The findings strongly support policy arguments for gender quotas in local governance, demonstrating that female leadership directly pivots fiscal priorities toward welfare-enhancing programs and downstream poverty alleviation.

---

## 🧰 Methodology
The empirical framework relies on a **Two-Way Fixed Effects (TWFE)** event-study model, supplemented by the **Callaway and Sant'Anna (2021)** estimator to correct for heterogeneous treatment effects across staggered rollouts.

Heterogeneity analysis was conducted by cross-referencing COMELEC electoral records with the Philippine Center for Investigative Journalism (PCIJ) political families database, coding dynastic transitions based on surname continuity (up to the second degree of consanguinity) with immediate predecessors or term-limited incumbents.

---

## 📂 Data Sources
The balanced panel merges four distinct datasets spanning 77 Philippine provinces from 1992 to 2022:
* **Bureau of Local Government Finance (BLGF):** Annual fiscal reports detailing health expenditure, public welfare expenditure, Internal Revenue Allotment (IRA), and local revenues.
* **Commission on Elections (COMELEC):** Provincial election outcomes, governor gender, and political competition metrics (Effective Number of Candidates).
* **PCIJ Political Families Database:** Proxy data for coding dynastic political succession.
* **PHILSA:** Administrative shapefiles utilized for spatial reference and network mapping.

---

## 💻 Replication & Usage
This project is built using Python for data processing/econometrics and LaTeX for manuscript compilation. The scripts are optimized for Linux-based operating systems.

### 1. Clone the Repository
```bash
git clone [https://github.com/KINGSTING/female-governor-spending.git](https://github.com/KINGSTING/female-governor-spending.git)
cd female-governor-spending
```

### 2. Set Up the Virtual Environment

To isolate project dependencies, create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages (e.g., pandas, statsmodels, matplotlib, jupyterlab):
```bash
pip install -r requirements.txt
```
(Note: Ensure your venv/ folder remains untracked by Git, as configured in the .gitignore)4. Compile the Manuscript

The final manuscript is written in LaTeX. To compile the PDF:
```bash
cd manuscript
pdflatex female_governors_spending.tex
bibtex female_governors_spending
pdflatex female_governors_spending.tex
pdflatex female_governors_spending.tex
```

## 🧑‍💻 Author
**Jemar John J. Lumingkit**
* Mindanao State University – Iligan Institute of Technology (MSU-IIT)
* **Email:** jemarjohn.lumingkit@msu.edu.ph
* **Research Interests:** Computational Policy Modeling, Deep Reinforcement Learning, Digital Governance, Public Administration.