# 🥗 NLP Meal Quality Assistant

An end-to-end agentic pipeline built in [Zerve](https://zerve.ai) that:

1. **Loads** real USDA nutrition data (333 foods)
2. **Scores** 5 meals 0–100 based on protein, fibre, saturated fat, and calories
3. **Visualises** meal scores and macro breakdowns
4. **Answers** plain-English questions via a keyword-based NLP assistant
5. **Generates** actionable health improvement tips per meal

## Project Structure

```
NLP_Meal_Assistant/
├── src/
│   ├── 01_load_nutrition_data.py      # Download & clean USDA dataset
│   ├── 02_meal_quality_scorer.py      # Score 5 meals 0-100
│   ├── 03_meal_charts.py              # Visualise scores & macros
│   ├── 04_health_insight_summary.py   # Per-meal tips & key takeaway
│   ├── 05_nlp_assistant.py            # NLP intent + answer engine
│   └── 06_demo_queries.py             # Run 10 demo questions
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
python src/01_load_nutrition_data.py
python src/02_meal_quality_scorer.py
python src/05_nlp_assistant.py
```

## Example Queries

```python
ask("What is the healthiest meal?")
ask("Why is the burger rated so poorly?")
ask("Compare chicken vs burger")
ask("How can I improve the oatmeal?")
ask("Which meal has the most fibre?")
```

## Scoring Model

| Factor | Weight | Direction |
|---|---|---|
| Protein (target 35g) | +30 pts | Reward |
| Fibre (target 8g) | +30 pts | Reward |
| Saturated fat (>5g) | −20 pts | Penalty |
| Calories (>700 kcal) | −20 pts | Penalty |

## Key Finding

> The biggest gap between a good and poor meal is **NOT calories** — it's **fibre and saturated fat**.
