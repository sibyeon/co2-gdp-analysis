# 🌍 CO₂ Emissions vs GDP per Capita (1990–2020)

**By Sang In Byeon** | ASU Data Science | DAT 301

## 🔗 Live App
👉 [Click here to view the live interactive app](https://co2-gdp-analysis-nkvgxmpxgxhclhvrpxcgqd.streamlit.app/)

## 📌 Project Overview
This project explores the relationship between a country's wealth (GDP per capita) and its carbon emissions (CO₂ per capita) across 165 countries from 1990 to 2020.

This repository contains **two versions** of the same analysis:
- `DAT301PROJ1FINAL.R` / `.Rmd` — Original analysis built in R (DAT 301 coursework)
- `app.py` — Enhanced interactive version rebuilt in Python using Streamlit

## 🔄 What I Improved in the Enhanced Version
| Feature | R Original | Python Enhanced |
|---|---|---|
| Interactivity | Static HTML | Live filters, sliders |
| Visualizations | ggplot2 (static) | Plotly (hover, zoom, pan) |
| Deployment | Local render only | Live public URL |
| Outlier handling | None | Top 0.1% removed |
| Color scheme | Default ggplot | Region-based with gradient |
| Data source | World Bank API | OWID (more reliable) |

## 🛠️ Tech Stack
- **Python** — Pandas, NumPy, Plotly, Streamlit
- **R** — ggplot2, dplyr, tidyr (original version)
- **Data** — Our World in Data (OWID) CO₂ dataset
- **Deployment** — Streamlit Community Cloud

## 💡 Key Findings
- Wealthier countries emit significantly more CO₂ per capita, but the relationship flattens at high income levels
- Middle Eastern nations (Qatar, Kuwait, UAE) dominate per capita emissions driven by oil economies
- Several high-income European countries have steadily reduced emissions since 2000
- Asia shows the widest spread — ranging from very low emitters to some of the highest in the world

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```