
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="🥗 Meal NLP Assistant", layout="wide", page_icon="🥗")

# ─── Data ─────────────────────────────────────────────────────────────────────
MANUAL_NUTRITION = {
    "Chicken, broilers or fryers": (165, 31.0, 3.6, 1.0, 0.0, 0.0),
    "Rice, white, cooked":         (130,  2.7, 0.3, 0.1, 0.4, 28.0),
    "Cola beverages":              ( 41,  0.0, 0.0, 0.0, 0.0, 10.6),
    "Strawberry jam":              (250,  0.4, 0.1, 0.0, 1.0, 65.0),
    "White bread":                 (265,  9.0, 3.2, 0.7, 2.7, 49.0),
    "Broccoli":                    ( 34,  2.8, 0.4, 0.0, 2.6,  6.6),
    "Hamburger":                   (295, 17.0,17.0, 6.5, 0.5, 24.0),
    "Potato chips":                (536,  7.0,35.0, 3.5, 4.4, 53.0),
    "Oatmeal":                     (371, 13.0, 6.5, 1.2,10.0, 67.0),
    "Banana":                      ( 89,  1.1, 0.3, 0.1, 2.6, 23.0),
    "Cows milk":                   ( 61,  3.2, 3.3, 2.1, 0.0,  4.8),
    "Butter":                      (717,  0.9,81.0,51.4, 0.0,  0.1),
    "Eggs raw":                    (143, 12.6, 9.5, 3.1, 0.0,  0.7),
    "Spinach":                     ( 23,  2.9, 0.4, 0.1, 2.2,  3.6),
    "Whole-wheat bread":           (247,  9.4, 3.4, 0.7, 6.0, 48.0),
}

MEALS = {
    "🍗 Grilled Chicken + Rice + Broccoli": [
        ("Chicken, broilers or fryers", 150),
        ("Rice, white, cooked", 120),
        ("Broccoli", 100),
    ],
    "🍔 Burger + Chips + Cola": [
        ("Hamburger", 200),
        ("Potato chips", 100),
        ("Cola beverages", 350),
    ],
    "🥣 Oatmeal + Banana + Milk": [
        ("Oatmeal", 80),
        ("Banana", 120),
        ("Cows milk", 200),
    ],
    "🍞 White Bread + Butter + Jam": [
        ("White bread", 80),
        ("Butter", 20),
        ("Strawberry jam", 30),
    ],
    "🥚 Egg + Spinach + Whole Wheat Toast": [
        ("Eggs raw", 120),
        ("Spinach", 80),
        ("Whole-wheat bread", 60),
    ],
}

def get_macros(meal_name):
    ingredients = MEALS[meal_name]
    totals = dict(calories_kcal=0.0, protein_g=0.0, fat_g=0.0,
                  sat_fat_g=0.0, fiber_g=0.0, carbs_g=0.0)
    for food, grams in ingredients:
        if food in MANUAL_NUTRITION:
            c,p,f,sf,fi,cb = MANUAL_NUTRITION[food]
            s = grams / 100
            totals["calories_kcal"] += c*s
            totals["protein_g"]     += p*s
            totals["fat_g"]         += f*s
            totals["sat_fat_g"]     += sf*s
            totals["fiber_g"]       += fi*s
            totals["carbs_g"]       += cb*s
    return totals

def score_meal(m):
    protein  = m["protein_g"]
    fibre    = m["fiber_g"]
    sat_fat  = m["sat_fat_g"]
    calories = m["calories_kcal"]
    s = (min(protein/35*30, 30) + min(fibre/8*30, 30)
         - min(max(sat_fat-5, 0)/10*20, 20)
         - min(max(calories-700, 0)/500*20, 20))
    return round(float(max(min(s, 100), 0)), 1)

@st.cache_data
def build_meal_scores():
    rows = []
    for meal_name in MEALS:
        m = get_macros(meal_name)
        score = score_meal(m)
        band  = ("🔴 Poor" if score < 25 else "🟡 Okay" if score < 50
                 else "🟢 Good" if score < 75 else "🌟 Excellent")
        rows.append({"meal": meal_name, "score": score, "band": band, **{k: round(v,1) for k,v in m.items()}})
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

meal_scores = build_meal_scores()

# ─── NLP ──────────────────────────────────────────────────────────────────────
INTENT_MAP = {
    "score":   ["score","rating","rate","ranked","rank","quality","how good","points"],
    "best":    ["best","healthiest","top","recommend","should i eat","what to eat"],
    "worst":   ["worst","unhealthiest","bad","avoid","dangerous"],
    "compare": ["vs","versus","compare","better","healthier","difference","between"],
    "macro":   ["protein","fibre","fiber","fat","calories","calorie","carbs","saturated","macro","nutrition","nutrient"],
    "why":     ["why","reason","explain","because","cause"],
    "list":    ["list","all","show","meals","what meals","available"],
    "improve": ["improve","boost","increase","fix","how can","what can"],
}
MEAL_ALIASES = {
    "chicken":"🍗 Grilled Chicken + Rice + Broccoli","rice":"🍗 Grilled Chicken + Rice + Broccoli",
    "broccoli":"🍗 Grilled Chicken + Rice + Broccoli","burger":"🍔 Burger + Chips + Cola",
    "chips":"🍔 Burger + Chips + Cola","cola":"🍔 Burger + Chips + Cola","junk":"🍔 Burger + Chips + Cola",
    "oatmeal":"🥣 Oatmeal + Banana + Milk","oats":"🥣 Oatmeal + Banana + Milk",
    "banana":"🥣 Oatmeal + Banana + Milk","milk":"🥣 Oatmeal + Banana + Milk",
    "bread":"🍞 White Bread + Butter + Jam","butter":"🍞 White Bread + Butter + Jam",
    "jam":"🍞 White Bread + Butter + Jam","toast":"🥚 Egg + Spinach + Whole Wheat Toast",
    "egg":"🥚 Egg + Spinach + Whole Wheat Toast","spinach":"🥚 Egg + Spinach + Whole Wheat Toast",
    "wheat":"🥚 Egg + Spinach + Whole Wheat Toast",
}
NUTRIENT_ALIASES = {
    "protein":"protein_g","fibre":"fiber_g","fiber":"fiber_g","fat":"fat_g",
    "saturated":"sat_fat_g","calories":"calories_kcal","calorie":"calories_kcal",
    "carbs":"carbs_g","carbohydrates":"carbs_g",
}
NUTRIENT_LABELS = {"protein_g":"protein","fiber_g":"fibre","fat_g":"fat",
                   "sat_fat_g":"sat. fat","calories_kcal":"calories","carbs_g":"carbs"}
NUTRIENT_UNITS  = {"protein_g":"g","fiber_g":"g","fat_g":"g",
                   "sat_fat_g":"g","calories_kcal":"kcal","carbs_g":"g"}

def detect_intent(text):
    tl = text.lower()
    hits = {i: sum(1 for kw in kws if kw in tl) for i, kws in INTENT_MAP.items()}
    hits = {i:v for i,v in hits.items() if v>0}
    return max(hits, key=hits.get) if hits else "unknown"

def detect_meals(text):
    tl = text.lower(); seen, found = set(), []
    for alias, meal in MEAL_ALIASES.items():
        if alias in tl and meal not in seen:
            found.append(meal); seen.add(meal)
    return found

def detect_nutrient(text):
    tl = text.lower()
    return next((col for alias, col in NUTRIENT_ALIASES.items() if alias in tl), None)

def ask(question, df=None):
    if df is None: df = meal_scores
    intent = detect_intent(question)
    meals  = detect_meals(question)
    nut    = detect_nutrient(question)
    if intent == "score":
        rows = (df[df["meal"].isin(meals)] if meals else df).sort_values("score", ascending=False)
        return "**Meal scores:**\n" + "\n".join(f"- {r['band']} **{r['meal']}** — {r['score']}/100" for _,r in rows.iterrows())
    elif intent == "best":
        r = df.loc[df["score"].idxmax()]
        return f"🏆 **Healthiest:** {r['meal']} ({r['score']}/100)\n- Protein: {r['protein_g']}g | Fibre: {r['fiber_g']}g | Sat.fat: {r['sat_fat_g']}g | {r['calories_kcal']:.0f} kcal"
    elif intent == "worst":
        r = df.loc[df["score"].idxmin()]
        return f"⚠️ **Least healthy:** {r['meal']} ({r['score']}/100)\n- {r['calories_kcal']:.0f} kcal | Sat.fat: {r['sat_fat_g']}g | Fibre only {r['fiber_g']}g"
    elif intent == "compare":
        if len(meals) < 2:
            return "Mention two meals to compare — e.g. *compare chicken vs burger*."
        a,b = df[df["meal"]==meals[0]].iloc[0], df[df["meal"]==meals[1]].iloc[0]
        w = a if a["score"]>b["score"] else b
        return (f"**Comparison:**\n- {a['meal']}: {a['score']}/100 | {a['calories_kcal']:.0f} kcal | {a['protein_g']}g protein\n"
                f"- {b['meal']}: {b['score']}/100 | {b['calories_kcal']:.0f} kcal | {b['protein_g']}g protein\n"
                f"\n🏆 **Winner:** {w['meal']} by {abs(a['score']-b['score']):.1f} pts")
    elif intent == "macro" and nut:
        label, unit = NUTRIENT_LABELS[nut], NUTRIENT_UNITS[nut]
        rows = (df[df["meal"].isin(meals)] if meals else df).sort_values(nut, ascending=False)
        return f"**{label.capitalize()} per meal:**\n" + "\n".join(f"- {r['meal']}: {r[nut]}{unit}" for _,r in rows.iterrows())
    elif intent == "why":
        if not meals: return "Which meal? e.g. *why is the burger rated poorly?*"
        r = df[df["meal"]==meals[0]].iloc[0]; reasons=[]
        if r["sat_fat_g"]>5:       reasons.append(f"high sat.fat ({r['sat_fat_g']}g)")
        if r["calories_kcal"]>700: reasons.append(f"too many calories ({r['calories_kcal']:.0f} kcal)")
        if r["protein_g"]<20:      reasons.append(f"low protein ({r['protein_g']}g)")
        if r["fiber_g"]<5:         reasons.append(f"low fibre ({r['fiber_g']}g)")
        if not reasons: reasons.append("misses reward thresholds slightly")
        return f"**{r['meal']}** scores {r['score']}/100 because: {', '.join(reasons)}."
    elif intent == "improve":
        if not meals: return "Which meal? e.g. *how can I improve the burger?*"
        r = df[df["meal"]==meals[0]].iloc[0]; tips=[]
        if r["fiber_g"]<5:         tips.append("add vegetables or legumes for fibre")
        if r["protein_g"]<25:      tips.append("add lean protein — chicken, eggs, or legumes")
        if r["sat_fat_g"]>5:       tips.append("cut butter, cheese, or fatty meat")
        if r["calories_kcal"]>700: tips.append("reduce portions or swap high-calorie items")
        if not tips: tips.append("already well balanced — keep it up!")
        return f"**Tips for {r['meal']}:**\n" + "\n".join(f"- {t}" for t in tips)
    elif intent == "list":
        return "**Available meals:**\n" + "\n".join(f"{i+1}. {r['meal']} ({r['score']}/100)" for i,(_,r) in enumerate(df.sort_values("score",ascending=False).iterrows()))
    elif nut:
        label, unit = NUTRIENT_LABELS[nut], NUTRIENT_UNITS[nut]
        rows = df.sort_values(nut, ascending=False)
        return f"**{label.capitalize()} per meal:**\n" + "\n".join(f"- {r['meal']}: {r[nut]}{unit}" for _,r in rows.iterrows())
    else:
        return ("I did not understand that. Try:\n"
                "- *What is the healthiest meal?*\n"
                "- *Why is the burger bad?*\n"
                "- *Compare chicken vs burger*\n"
                "- *How much protein does each meal have?*\n"
                "- *How can I improve the oatmeal?*")

# ─── Layout ───────────────────────────────────────────────────────────────────
st.title("🥗 NLP Meal Assistant")
st.caption("Ask any question about meals in plain English — powered by keyword NLP + USDA nutrition data.")

col1, col2 = st.columns([1.2, 2], gap="large")

with col1:
    st.subheader("📊 Meal Scores")
    colours = {"🔴 Poor":"#f04438","🟡 Okay":"#ffd400","🟢 Good":"#8DE5A1","🌟 Excellent":"#17b26a"}
    fig, ax = plt.subplots(figsize=(5,4))
    fig.patch.set_facecolor("#1D1D20")
    ax.set_facecolor("#1D1D20")
    short = [m.split("+")[0].strip() for m in meal_scores["meal"]]
    bar_colours = [colours.get(b,"#A1C9F4") for b in meal_scores["band"]]
    bars = ax.barh(short, meal_scores["score"], color=bar_colours, height=0.55)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score / 100", color="#909094", fontsize=9)
    ax.tick_params(colors="#fbfbff", labelsize=8)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.xaxis.label.set_color("#909094")
    for bar_, score in zip(bars, meal_scores["score"]):
        ax.text(bar_.get_width()+1, bar_.get_y()+bar_.get_height()/2,
                f"{score}", va="center", color="#fbfbff", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("🔬 Macro Breakdown")
    macro_cols = ["protein_g","fiber_g","sat_fat_g","calories_kcal"]
    display_df = meal_scores[["meal","score"]+macro_cols].copy()
    display_df.columns = ["Meal","Score","Protein(g)","Fibre(g)","Sat.Fat(g)","Calories(kcal)"]
    display_df["Meal"] = display_df["Meal"].str.replace(r"^\S+ ", "", regex=True)
    st.dataframe(display_df.set_index("Meal"), use_container_width=True)

with col2:
    st.subheader("💬 Ask the Assistant")
    example_qs = [
        "What is the healthiest meal?",
        "Why is the burger bad?",
        "Compare chicken vs burger",
        "How much protein does each meal have?",
        "How can I improve the oatmeal?",
        "Which meal has the most fibre?",
        "What are the worst meals to avoid?",
        "Show me all meal scores",
    ]
    chosen = st.selectbox("💡 Try an example question:", ["(type your own below)"] + example_qs)
    user_q = st.text_input("Or type your own question:", value="" if chosen=="(type your own below)" else chosen, placeholder="e.g. How can I improve the burger?")
    if user_q.strip():
        answer = ask(user_q)
        st.markdown("---")
        st.markdown("**🤖 Answer:**")
        st.markdown(answer)

    st.markdown("---")
    st.subheader("📋 All Meals at a Glance")
    for _, row in meal_scores.iterrows():
        with st.expander(f"{row['band']}  {row['meal']}  —  {row['score']}/100"):
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Calories", f"{row['calories_kcal']:.0f} kcal")
            c2.metric("Protein",  f"{row['protein_g']}g")
            c3.metric("Fibre",    f"{row['fiber_g']}g")
            c4.metric("Sat.Fat",  f"{row['sat_fat_g']}g")
            c5.metric("Carbs",    f"{row['carbs_g']}g")
