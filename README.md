# 🥗 NLP Meal Assistant

An agentic project that scores meals on nutrition quality and answers natural-language queries.

## 🚀 Live Demo (Streamlit)
```
streamlit run app.py
```

## 📁 Structure
```
NLP_Meal_Assistant/
├── app.py                    ← Streamlit live demo
├── requirements.txt
├── README.md
└── src/
    ├── 01_load_nutrition_data.py
    ├── 02_meal_quality_scorer.py
    ├── 03_meal_charts.py
    ├── 04_health_insight_summary.py
    ├── 05_nlp_assistant.py
    └── 06_demo_queries.py
```

## 💡 Features
- 🥗 Scores 5 meals on protein, fibre, sat.fat & calories
- 💬 NLP assistant — ask questions in plain English
- 📊 Interactive bar chart + macro breakdown table
- 🔍 Intent detection across 8 query types

## 🛠️ Run locally
```bash
git clone https://github.com/Shailareddy2716/NLP_Meal_Assistant.git
cd NLP_Meal_Assistant
pip install -r requirements.txt
streamlit run app.py
```
