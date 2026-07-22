
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

MEAL_NAMES = list(MEALS.keys())
DAILY_TARGET = 2000  # kcal

def get_macros(meal_name):
    totals = dict(calories_kcal=0.0, protein_g=0.0, fat_g=0.0,
                  sat_fat_g=0.0, fiber_g=0.0, carbs_g=0.0)
    for food, grams in MEALS[meal_name]:
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
    s = (min(m["protein_g"]/35*30, 30) + min(m["fiber_g"]/8*30, 30)
         - min(max(m["sat_fat_g"]-5, 0)/10*20, 20)
         - min(max(m["calories_kcal"]-700, 0)/500*20, 20))
    return round(float(max(min(s, 100), 0)), 1)

@st.cache_data
def build_meal_scores():
    rows = []
    for meal_name in MEALS:
        m = get_macros(meal_name)
        score = score_meal(m)
        band  = ("🔴 Poor" if score < 25 else "🟡 Okay" if score < 50
                 else "🟢 Good" if score < 75 else "🌟 Excellent")
        rows.append({"meal": meal_name, "score": score, "band": band,
                     **{k: round(v,1) for k,v in m.items()}})
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

meal_scores = build_meal_scores()

# ─── Calorie colour helper ────────────────────────────────────────────────────
def calorie_colour_meal(kcal, target=700):
    pct = kcal / target
    if pct <= 0.75:  return "#17b26a"
    elif pct <= 1.0: return "#ffd400"
    else:            return "#f04438"

def render_calorie_visual(meals_subset):
    df = meal_scores[meal_scores["meal"].isin(meals_subset)].sort_values(
            "calories_kcal", ascending=True)
    fig, ax = plt.subplots(figsize=(6, max(2.5, 0.7 * len(df))))
    fig.patch.set_facecolor("#1D1D20")
    ax.set_facecolor("#1D1D20")
    short  = [m.split("+")[0].strip()[:22] for m in df["meal"]]
    kcals  = df["calories_kcal"].tolist()
    colours = [calorie_colour_meal(k) for k in kcals]
    max_bar = max(max(kcals) * 1.15, 700 * 1.1)
    ax.barh(short, [max_bar]*len(short), color="#2a2a2e", height=0.55, zorder=1)
    bars = ax.barh(short, kcals, color=colours, height=0.55, zorder=2)
    ax.axvline(700, color="#fbfbff", linewidth=1.2, linestyle="--", alpha=0.6, zorder=3)
    ax.text(708, len(df)-0.4, "Target 700 kcal", color="#909094", fontsize=7.5, va="top")
    for bar_, kcal in zip(bars, kcals):
        ax.text(bar_.get_width()+10, bar_.get_y()+bar_.get_height()/2,
                f"{kcal:.0f} kcal", va="center", color="#fbfbff", fontsize=8.5, fontweight="bold")
    ax.set_xlim(0, max_bar*1.18)
    ax.set_xlabel("Calories (kcal)", color="#909094", fontsize=9)
    ax.tick_params(colors="#fbfbff", labelsize=8.5)
    for spine in ax.spines.values(): spine.set_visible(False)
    patches = [
        mpatches.Patch(color="#17b26a", label="Under target"),
        mpatches.Patch(color="#ffd400", label="Near target"),
        mpatches.Patch(color="#f04438", label="Over target"),
    ]
    ax.legend(handles=patches, loc="lower right", fontsize=7.5,
              facecolor="#1D1D20", edgecolor="#444", labelcolor="#fbfbff")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ─── Daily tracker chart ─────────────────────────────────────────────────────
def render_daily_tracker(slot_meals):
    SLOT_COLOURS = {
        "Breakfast": "#A1C9F4",
        "Lunch":     "#8DE5A1",
        "Dinner":    "#FFB482",
        "Snack":     "#D0BBFF",
    }
    slots_with_meals = {s: m for s, m in slot_meals.items() if m}
    if not slots_with_meals:
        st.info("Select at least one meal above to see your daily tracker.")
        return

    slot_kcals   = {}
    slot_protein = {}
    slot_fibre   = {}
    for slot, meal in slots_with_meals.items():
        macros = get_macros(meal)
        slot_kcals[slot]   = macros["calories_kcal"]
        slot_protein[slot] = macros["protein_g"]
        slot_fibre[slot]   = macros["fiber_g"]

    total_kcal = sum(slot_kcals.values())
    pct = min(total_kcal / DAILY_TARGET, 1.0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5),
                                    gridspec_kw={"width_ratios": [2.5, 1]})
    fig.patch.set_facecolor("#1D1D20")

    # Left: stacked horizontal bar
    ax1.set_facecolor("#1D1D20")
    ax1.barh(["Daily total"], [DAILY_TARGET * 1.25], color="#2a2a2e", height=0.5)

    left = 0
    for slot, kcal in slot_kcals.items():
        colour = SLOT_COLOURS.get(slot, "#fbfbff")
        ax1.barh(["Daily total"], [kcal], left=left, color=colour,
                 height=0.5, label=f"{slot}: {kcal:.0f} kcal")
        if kcal > 80:
            ax1.text(left + kcal/2, 0, f"{slot}\n{kcal:.0f}", ha="center",
                     va="center", color="#1D1D20", fontsize=8, fontweight="bold")
        left += kcal

    ax1.axvline(DAILY_TARGET, color="#fbfbff", linewidth=1.5,
                linestyle="--", alpha=0.7, zorder=5)
    ax1.text(DAILY_TARGET + 15, 0.28, "2000 kcal target",
             color="#909094", fontsize=8, va="top")

    if total_kcal > DAILY_TARGET:
        ax1.axvline(total_kcal, color="#f04438", linewidth=1.5, alpha=0.8, zorder=6)
        ax1.text(total_kcal + 15, -0.28,
                 f"+{total_kcal - DAILY_TARGET:.0f} over",
                 color="#f04438", fontsize=8, va="bottom")

    ax1.set_xlim(0, max(DAILY_TARGET * 1.3, total_kcal * 1.15))
    ax1.set_xlabel("Calories (kcal)", color="#909094", fontsize=9)
    ax1.set_title("Calorie breakdown by meal slot", color="#fbfbff", fontsize=10, pad=8)
    ax1.tick_params(colors="#fbfbff", labelsize=8.5)
    for spine in ax1.spines.values(): spine.set_visible(False)
    ax1.legend(loc="lower right", fontsize=7.5,
               facecolor="#1D1D20", edgecolor="#444", labelcolor="#fbfbff")

    # Right: donut gauge
    ax2.set_facecolor("#1D1D20")
    ax2.set_aspect("equal")
    gauge_colour = ("#17b26a" if total_kcal <= DAILY_TARGET * 0.75 else
                    "#ffd400" if total_kcal <= DAILY_TARGET else "#f04438")
    sizes  = [pct, 1 - pct]
    colours_donut = [gauge_colour, "#2a2a2e"]
    ax2.pie(sizes, colors=colours_donut, startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.38, edgecolor="#1D1D20"))
    ax2.text(0, 0.08, f"{total_kcal:.0f}", ha="center", va="center",
             color="#fbfbff", fontsize=16, fontweight="bold")
    ax2.text(0, -0.22, "kcal today", ha="center", va="center",
             color="#909094", fontsize=8)
    pct_label = f"{total_kcal/DAILY_TARGET*100:.0f}% of daily goal"
    ax2.text(0, -0.55, pct_label, ha="center", va="center",
             color=gauge_colour, fontsize=8, fontweight="bold")
    ax2.set_title("Daily gauge", color="#fbfbff", fontsize=10, pad=8)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    total_protein = sum(slot_protein.values())
    total_fibre   = sum(slot_fibre.values())
    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Total Calories", f"{total_kcal:.0f} kcal",
              delta=f"{total_kcal - DAILY_TARGET:+.0f} vs target")
    c2.metric("💪 Total Protein",  f"{total_protein:.1f} g",
              delta="target ~140g" if total_protein < 140 else "✅ on track")
    c3.metric("🌿 Total Fibre",    f"{total_fibre:.1f} g",
              delta="target ~30g"  if total_fibre  < 30  else "✅ on track")


# ─── NLP ──────────────────────────────────────────────────────────────────────
INTENT_MAP = {
    "score":   ["score","rating","rate","ranked","rank","quality","how good","points"],
    "best":    ["best","healthiest","top","recommend","should i eat","what to eat"],
    "worst":   ["worst","unhealthiest","bad","avoid","dangerous"],
    "compare": ["vs","versus","compare","better","healthier","difference","between"],
    "calorie": ["calories","calorie","kcal","energy","how much am i eating",
                "how many calories","caloric","cal"],
    "macro":   ["protein","fibre","fiber","fat","carbs","saturated","macro","nutrition","nutrient"],
    "why":     ["why","reason","explain","because","cause"],
    "list":    ["list","all","show","meals","what meals","available"],
    "improve": ["improve","boost","increase","fix","how can","what can"],
}
MEAL_ALIASES = {
    "chicken": "🍗 Grilled Chicken + Rice + Broccoli",
    "rice":    "🍗 Grilled Chicken + Rice + Broccoli",
    "broccoli":"🍗 Grilled Chicken + Rice + Broccoli",
    "burger":  "🍔 Burger + Chips + Cola",
    "chips":   "🍔 Burger + Chips + Cola",
    "cola":    "🍔 Burger + Chips + Cola",
    "junk":    "🍔 Burger + Chips + Cola",
    "oatmeal": "🥣 Oatmeal + Banana + Milk",
    "oats":    "🥣 Oatmeal + Banana + Milk",
    "banana":  "🥣 Oatmeal + Banana + Milk",
    "milk":    "🥣 Oatmeal + Banana + Milk",
    "bread":   "🍞 White Bread + Butter + Jam",
    "butter":  "🍞 White Bread + Butter + Jam",
    "jam":     "🍞 White Bread + Butter + Jam",
    "toast":   "🥚 Egg + Spinach + Whole Wheat Toast",
    "egg":     "🥚 Egg + Spinach + Whole Wheat Toast",
    "spinach": "🥚 Egg + Spinach + Whole Wheat Toast",
    "wheat":   "🥚 Egg + Spinach + Whole Wheat Toast",
}
NUTRIENT_ALIASES = {
    "protein":"protein_g","fibre":"fiber_g","fiber":"fiber_g","fat":"fat_g",
    "saturated":"sat_fat_g","sat fat":"sat_fat_g","carbs":"carbs_g",
    "calories":"calories_kcal","calorie":"calories_kcal","kcal":"calories_kcal",
}
NUTRIENT_LABELS = {
    "protein_g":"Protein","fiber_g":"Fibre","fat_g":"Fat",
    "sat_fat_g":"Sat.Fat","carbs_g":"Carbs","calories_kcal":"Calories",
}
NUTRIENT_UNITS = {
    "protein_g":"g","fiber_g":"g","fat_g":"g",
    "sat_fat_g":"g","carbs_g":"g","calories_kcal":"kcal",
}

def detect_intent(q):
    q = q.lower()
    for intent, keywords in INTENT_MAP.items():
        if any(kw in q for kw in keywords):
            return intent
    return "list"

def detect_meals(q):
    q = q.lower()
    found = []
    for alias, meal in MEAL_ALIASES.items():
        if alias in q and meal not in found:
            found.append(meal)
    return found if found else list(meal_scores["meal"])

def detect_nutrient(q):
    q = q.lower()
    for alias, col in NUTRIENT_ALIASES.items():
        if alias in q:
            return col
    return None

def answer_score(meals):
    rows = meal_scores[meal_scores["meal"].isin(meals)].sort_values("score", ascending=False)
    lines = [f"  {r.band}  {r.meal}  —  {r.score}/100" for _, r in rows.iterrows()]
    return "**Meal Quality Scores:**\n" + "\n".join(lines)

def answer_best(_meals):
    r = meal_scores.iloc[0]
    m = get_macros(r["meal"])
    return (f"**Healthiest meal:** {r.meal}  ({r.score}/100)\n"
            f"  Protein: {m['protein_g']:.1f}g  |  Fibre: {m['fiber_g']:.1f}g  "
            f"|  Calories: {m['calories_kcal']:.0f} kcal")

def answer_worst(_meals):
    r = meal_scores.iloc[-1]
    m = get_macros(r["meal"])
    return (f"**Worst meal:** {r.meal}  ({r.score}/100)\n"
            f"  Calories: {m['calories_kcal']:.0f} kcal  |  "
            f"Sat.Fat: {m['sat_fat_g']:.1f}g  |  Fibre: {m['fiber_g']:.1f}g")

def answer_compare(meals):
    if len(meals) < 2:
        meals = list(meal_scores["meal"])[:2]
    a = meal_scores[meal_scores["meal"]==meals[0]].iloc[0]
    b = meal_scores[meal_scores["meal"]==meals[1]].iloc[0]
    winner, loser = (a, b) if a.score >= b.score else (b, a)
    diff = abs(a.score - b.score)
    return (f"**{winner.meal}** wins by {diff:.1f} pts\n"
            f"  {winner.meal}: {winner.score}/100\n"
            f"  {loser.meal}:  {loser.score}/100")

def answer_macro(meals, nutrient):
    col = nutrient or "protein_g"
    label = NUTRIENT_LABELS.get(col, col)
    unit  = NUTRIENT_UNITS.get(col, "")
    rows = meal_scores[meal_scores["meal"].isin(meals)].sort_values(col, ascending=False)
    lines = [f"  {r.meal}: {r[col]:.1f} {unit}" for _, r in rows.iterrows()]
    return f"**{label} per meal:**\n" + "\n".join(lines)

def answer_why(meals):
    r = meal_scores[meal_scores["meal"].isin(meals)].iloc[0]
    issues = []
    if r.sat_fat_g > 5:  issues.append(f"high sat.fat ({r.sat_fat_g:.1f}g > 5g target)")
    if r.calories_kcal > 700: issues.append(f"high calories ({r.calories_kcal:.0f} > 700 kcal target)")
    if r.fiber_g < 4:    issues.append(f"low fibre ({r.fiber_g:.1f}g < 4g target)")
    if r.protein_g < 20: issues.append(f"low protein ({r.protein_g:.1f}g < 20g target)")
    if not issues:       issues = ["it actually scores reasonably well!"]
    return f"**Why {r.meal} scores {r.score}/100:**\n  " + "\n  ".join(issues)

def answer_improve(meals):
    r = meal_scores[meal_scores["meal"].isin(meals)].iloc[0]
    tips = []
    if r.fiber_g < 4:    tips.append("Add vegetables or legumes for more fibre")
    if r.protein_g < 20: tips.append("Add lean protein (chicken, eggs, Greek yogurt)")
    if r.sat_fat_g > 5:  tips.append("Reduce butter, cheese, or fatty meat")
    if r.calories_kcal > 700: tips.append("Reduce portion sizes or swap high-cal items")
    if not tips:         tips = ["This meal is already well-balanced!"]
    return f"**How to improve {r.meal}:**\n  " + "\n  ".join(tips)

def answer_list(_meals):
    lines = [f"  {i+1}. {r.meal}  ({r.score}/100)" for i, r in meal_scores.iterrows()]
    return "**Available meals:**\n" + "\n".join(lines)

INTENT_FN = {
    "score": answer_score, "best": answer_best, "worst": answer_worst,
    "compare": answer_compare, "calorie": answer_macro, "macro": answer_macro,
    "why": answer_why, "improve": answer_improve, "list": answer_list,
}

def ask(question):
    intent  = detect_intent(question)
    meals   = detect_meals(question)
    nutrient = detect_nutrient(question)
    if intent == "calorie":
        nutrient = "calories_kcal"
    fn = INTENT_FN.get(intent, answer_list)
    if intent in ("macro", "calorie"):
        return fn(meals, nutrient)
    return fn(meals)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🥗 Meal NLP Assistant")
st.sidebar.markdown("Ask anything about your meals — nutrition, scores, calories, tips.")
st.sidebar.divider()
st.sidebar.markdown("**5 meals tracked:**")
for _, r in meal_scores.iterrows():
    st.sidebar.markdown(f"{r.band}  {r['meal'].split(chr(32)+'+')[0]}  `{r.score}/100`")

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🍽️ Meal Scores", "🤖 NLP Assistant", "📅 Daily Tracker"])

# ── Tab 1: Meal Scores ─────────────────────────────────────────────────────────
with tab1:
    st.subheader("Meal Quality Scores")
    df_plot = meal_scores.sort_values("score")
    short_labels = [m.split("+")[0].strip()[:28] for m in df_plot["meal"]]
    BAND_COLOURS = {"🔴 Poor":"#f04438","🟡 Okay":"#ffd400",
                    "🟢 Good":"#17b26a","🌟 Excellent":"#A1C9F4"}
    bar_colours = [BAND_COLOURS.get(b, "#fbfbff") for b in df_plot["band"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#1D1D20")
    ax.set_facecolor("#1D1D20")
    bars = ax.barh(short_labels, df_plot["score"], color=bar_colours, height=0.55)
    for bar_, score in zip(bars, df_plot["score"]):
        ax.text(bar_.get_width()+0.8, bar_.get_y()+bar_.get_height()/2,
                f"{score}", va="center", color="#fbfbff", fontsize=9, fontweight="bold")
    ax.set_xlim(0, 115)
    ax.set_xlabel("Quality Score (0–100)", color="#909094", fontsize=9)
    ax.set_title("Meal Quality Scores", color="#fbfbff", fontsize=11, pad=10)
    ax.tick_params(colors="#fbfbff", labelsize=8.5)
    for spine in ax.spines.values(): spine.set_visible(False)
    patches = [mpatches.Patch(color=v, label=k) for k,v in BAND_COLOURS.items()]
    ax.legend(handles=patches, loc="lower right", fontsize=8,
              facecolor="#1D1D20", edgecolor="#444", labelcolor="#fbfbff")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()
    st.subheader("Macro Breakdown")
    display_cols = ["meal","score","calories_kcal","protein_g","fiber_g","sat_fat_g","carbs_g"]
    rename_map   = {"meal":"Meal","score":"Score","calories_kcal":"Kcal",
                    "protein_g":"Protein(g)","fiber_g":"Fibre(g)",
                    "sat_fat_g":"Sat.Fat(g)","carbs_g":"Carbs(g)"}
    st.dataframe(meal_scores[display_cols].rename(columns=rename_map), use_container_width=True)

# ── Tab 2: NLP Assistant ──────────────────────────────────────────────────────
with tab2:
    st.subheader("Ask the Meal Assistant")
    example_qs = [
        "-- pick an example --",
        "What is the healthiest meal?",
        "What is the worst meal and why?",
        "Compare chicken vs burger",
        "How many calories am I eating?",
        "How much protein does each meal have?",
        "Which meal has the most fibre?",
        "How can I improve the burger?",
        "Show me all meals",
    ]
    selected = st.selectbox("💡 Example questions:", example_qs)
    user_q = st.text_input("Or type your own question:", value="" if selected.startswith("--") else selected)
    if user_q:
        intent = detect_intent(user_q)
        meals  = detect_meals(user_q)
        answer = ask(user_q)
        st.markdown("---")
        st.markdown(f"**🤖 Answer:**\n\n{answer}")
        if intent == "calorie":
            st.markdown("---")
            st.markdown("**📊 Calorie Visual:**")
            render_calorie_visual(meals)

# ── Tab 3: Daily Tracker ──────────────────────────────────────────────────────
with tab3:
    st.subheader("📅 Daily Calorie Tracker")
    st.markdown("Pick a meal for each slot to see your daily total vs the 2000 kcal target.")

    SKIP = "— skip —"
    slot_options = [SKIP] + MEAL_NAMES

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        breakfast = st.selectbox("🌅 Breakfast", slot_options,
                                  index=slot_options.index("🥣 Oatmeal + Banana + Milk"))
    with col2:
        lunch = st.selectbox("☀️ Lunch", slot_options,
                              index=slot_options.index("🍗 Grilled Chicken + Rice + Broccoli"))
    with col3:
        dinner = st.selectbox("🌙 Dinner", slot_options, index=0)
    with col4:
        snack  = st.selectbox("🍎 Snack",  slot_options, index=0)

    slot_meals = {
        "Breakfast": None if breakfast == SKIP else breakfast,
        "Lunch":     None if lunch     == SKIP else lunch,
        "Dinner":    None if dinner    == SKIP else dinner,
        "Snack":     None if snack     == SKIP else snack,
    }

    st.divider()
    render_daily_tracker(slot_meals)

    st.divider()
    st.subheader("Meal Details")
    for slot, meal in slot_meals.items():
        if meal:
            m = get_macros(meal)
            with st.expander(f"{slot}: {meal}"):
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                mc1.metric("🔥 Calories", f"{m['calories_kcal']:.0f} kcal")
                mc2.metric("💪 Protein",  f"{m['protein_g']:.1f} g")
                mc3.metric("🌿 Fibre",    f"{m['fiber_g']:.1f} g")
                mc4.metric("🧈 Sat.Fat",  f"{m['sat_fat_g']:.1f} g")
                mc5.metric("🍞 Carbs",    f"{m['carbs_g']:.1f} g")
