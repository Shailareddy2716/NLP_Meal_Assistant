import re

INTENT_MAP = {
    "score":   ["score", "rating", "rate", "ranked", "rank", "quality", "how good", "points"],
    "best":    ["best", "healthiest", "top", "recommend", "should i eat", "what to eat"],
    "worst":   ["worst", "unhealthiest", "bad", "avoid", "dangerous"],
    "compare": ["vs", "versus", "compare", "better", "healthier", "difference", "between"],
    "macro":   ["protein", "fibre", "fiber", "fat", "calories", "carbs", "calorie",
                "saturated", "macro", "nutrition", "nutrient"],
    "why":     ["why", "reason", "explain", "because", "cause"],
    "list":    ["list", "all", "show", "meals", "what meals", "available"],
    "improve": ["improve", "boost", "increase", "fix", "how can", "what can"],
}

MEAL_ALIASES = {
    "chicken":  "Grilled Chicken + Rice + Broccoli",
    "rice":     "Grilled Chicken + Rice + Broccoli",
    "broccoli": "Grilled Chicken + Rice + Broccoli",
    "burger":   "Burger + Chips + Cola",
    "chips":    "Burger + Chips + Cola",
    "cola":     "Burger + Chips + Cola",
    "oatmeal":  "Oatmeal + Banana + Milk",
    "banana":   "Oatmeal + Banana + Milk",
    "milk":     "Oatmeal + Banana + Milk",
    "bread":    "White Bread + Butter + Jam",
    "butter":   "White Bread + Butter + Jam",
    "jam":      "White Bread + Butter + Jam",
    "toast":    "Egg + Spinach + Whole Wheat Toast",
    "egg":      "Egg + Spinach + Whole Wheat Toast",
    "spinach":  "Egg + Spinach + Whole Wheat Toast",
}

NUTRIENT_ALIASES = {
    "protein":  "protein_g", "fibre": "fiber_g", "fiber": "fiber_g",
    "fat":      "fat_g",     "saturated": "sat_fat_g",
    "calories": "calories_kcal", "calorie": "calories_kcal",
    "carbs":    "carbs_g",
}

def detect_intent(text):
    tl = text.lower()
    hits = {i: sum(1 for kw in kws if kw in tl) for i, kws in INTENT_MAP.items()}
    hits = {i: v for i, v in hits.items() if v > 0}
    return max(hits, key=hits.get) if hits else "unknown"

def detect_meals(text):
    tl = text.lower()
    seen, found = set(), []
    for alias, meal in MEAL_ALIASES.items():
        if alias in tl and meal not in seen:
            found.append(meal); seen.add(meal)
    return found

def detect_nutrient(text):
    tl = text.lower()
    return next((col for alias, col in NUTRIENT_ALIASES.items() if alias in tl), None)

def ask(question, meal_scores):
    intent   = detect_intent(question)
    meals    = detect_meals(question)
    nutrient = detect_nutrient(question)

    if intent == "best":
        r = meal_scores.loc[meal_scores["score"].idxmax()]
        return f"Healthiest: {r['meal']} ({r['score']}/100)"
    elif intent == "worst":
        r = meal_scores.loc[meal_scores["score"].idxmin()]
        return f"Least healthy: {r['meal']} ({r['score']}/100)"
    elif intent == "list":
        lines = [f"  {i+1}. {r['meal']} ({r['score']}/100)"
                 for i, (_, r) in enumerate(meal_scores.sort_values("score", ascending=False).iterrows())]
        return "Available meals:\n" + "\n".join(lines)
    else:
        return "Try: best, worst, list, compare X vs Y, why is X bad, how can I improve X"

print("NLP assistant loaded. Call ask(question, meal_scores).")
