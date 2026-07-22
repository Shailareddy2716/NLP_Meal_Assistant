
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
    ax.text(708, len(df)-0.4, "Target
700 kcal", color="#909094", fontsize=7.5, va="top")
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
    """
    slot_meals: dict  {slot_name: meal_name or None}
    Renders a stacked horizontal bar showing kcal per meal slot vs 2000 kcal daily target.
    Below that, a donut gauge showing % of daily target consumed.
    """
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

    # ── Left: stacked horizontal bar ─────────────────────────────────────────
    ax1.set_facecolor("#1D1D20")
    # background full-day track
    ax1.barh(["Daily total"], [DAILY_TARGET * 1.25], color="#2a2a2e", height=0.5)

    left = 0
    for slot, kcal in slot_kcals.items():
        colour = SLOT_COLOURS.get(slot, "#fbfbff")
        bar = ax1.barh(["Daily total"], [kcal], left=left, color=colour,
                       height=0.5, label=f"{slot}: {kcal:.0f} kcal")
        # label inside bar if wide enough
        if kcal > 80:
            ax1.text(left + kcal/2, 0, f"{slot}
{kcal:.0f}", ha="center",
                     va="center", color="#1D1D20", fontsize=8, fontweight="bold")
        left += kcal

    # target line
    ax1.axvline(DAILY_TARGET, color="#fbfbff", linewidth=1.5,
                linestyle="--", alpha=0.7, zorder=5)
    ax1.text(DAILY_TARGET + 15, 0.28, f"2000 kcal
target",
             color="#909094", fontsize=8, va="top")

    # over-target indicator
    if total_kcal > DAILY_TARGET:
        ax1.axvline(total_kcal, color="#f04438", linewidth=1.5, alpha=0.8, zorder=6)
        ax1.text(total_kcal + 15, -0.28,
                 f"+{total_kcal - DAILY_TARGET:.0f} over",
                 color="#f04438", fontsize=8, va="bottom")

    ax1.set_xlim(0, max(DAILY_TARGET * 1.3, total_kcal * 1.15))
    ax1.set_xlabel("Calories (kcal)", color="#909094", fontsize=9)
    ax1.set_title("Calorie breakdown by meal slot", color="#fbfbff",
                  fontsize=10, pad=8)
    ax1.tick_params(colors="#fbfbff", labelsize=8.5)
    for spine in ax1.spines.values(): spine.set_visible(False)
    ax1.legend(loc="lower right", fontsize=7.5,
               facecolor="#1D1D20", edgecolor="#444", labelcolor="#fbfbff")

    # ── Right: donut gauge ────────────────────────────────────────────────────
    ax2.set_facecolor("#1D1D20")
    ax2.set_aspect("equal")

    gauge_colour = ("#17b26a" if total_kcal <= DAILY_TARGET * 0.75 else
                    "#ffd400" if total_kcal <= DAILY_TARGET else "#f04438")
    sizes  = [pct, 1 - pct]
    colours_donut = [gauge_colour, "#2a2a2e"]
    wedges, _ = ax2.pie(sizes, colors=colours_donut, startangle=90,
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

    # ── Macro summary row ─────────────────────────────────────────────────────
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
    "saturated":"sat_fat_g","carbs":"carbs_g","carbohydrates":"carbs_g",
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

    if intent == "calorie":
        target_meals = meals if meals else df["meal"].tolist()
        subset = df[df["meal"].isin(target_meals)].sort_values("calories_kcal", ascending=False)
        lines = [f"- **{r['meal']}**: {r['calories_kcal']:.0f} kcal" for _,r in subset.iterrows()]
        text = "**Calories per meal** (vs 700 kcal target per meal):\n" + "\n".join(lines)
        return text, "calorie", target_meals

    if intent == "score":
        rows = (df[df["meal"].isin(meals)] if meals else df).sort_values("score", ascending=False)
        return ("**Meal scores:**\n" +
                "\n".join(f"- {r['band']} **{r['meal']}** — {r['score']}/100"
                           for _,r in rows.iterrows()), None, [])
    elif intent == "best":
        r = df.loc[df["score"].idxmax()]
        return (f"🏆 **Healthiest:** {r['meal']} ({r['score']}/100)\n"
                f"- Protein: {r['protein_g']}g | Fibre: {r['fiber_g']}g | "
                f"Sat.fat: {r['sat_fat_g']}g | {r['calories_kcal']:.0f} kcal"), None, []
    elif intent == "worst":
        r = df.loc[df["score"].idxmin()]
        return (f"⚠️ **Least healthy:** {r['meal']} ({r['score']}/100)\n"
                f"- {r['calories_kcal']:.0f} kcal | Sat.fat: {r['sat_fat_g']}g | "
                f"Fibre only {r['fiber_g']}g"), None, []
    elif intent == "compare":
        if len(meals) < 2:
            return "Mention two meals to compare — e.g. *compare chicken vs burger*.", None, []
        a,b = df[df["meal"]==meals[0]].iloc[0], df[df["meal"]==meals[1]].iloc[0]
        w = a if a["score"]>b["score"] else b
        return (f"**Comparison:**\n- {a['meal']}: {a['score']}/100 | "
                f"{a['calories_kcal']:.0f} kcal | {a['protein_g']}g protein\n"
                f"- {b['meal']}: {b['score']}/100 | {b['calories_kcal']:.0f} kcal | "
                f"{b['protein_g']}g protein\n"
                f"\n🏆 **Winner:** {w['meal']} by {abs(a['score']-b['score']):.1f} pts"), None, []
    elif intent == "macro" and nut:
        label, unit = NUTRIENT_LABELS[nut], NUTRIENT_UNITS[nut]
        rows = (df[df["meal"].isin(meals)] if meals else df).sort_values(nut, ascending=False)
        return (f"**{label.capitalize()} per meal:**\n" +
                "\n".join(f"- {r['meal']}: {r[nut]}{unit}"
                           for _,r in rows.iterrows()), None, [])
    elif intent == "why":
        if not meals: return "Which meal? e.g. *why is the burger rated poorly?*", None, []
        r = df[df["meal"]==meals[0]].iloc[0]; reasons=[]
        if r["sat_fat_g"]>5:       reasons.append(f"high sat.fat ({r['sat_fat_g']}g)")
        if r["calories_kcal"]>700: reasons.append(f"too many calories ({r['calories_kcal']:.0f} kcal)")
        if r["protein_g"]<20:      reasons.append(f"low protein ({r['protein_g']}g)")
        if r["fiber_g"]<5:         reasons.append(f"low fibre ({r['fiber_g']}g)")
        if not reasons: reasons.append("misses reward thresholds slightly")
        return f"**{r['meal']}** scores {r['score']}/100 because: {', '.join(reasons)}.", None, []
    elif intent == "improve":
        if not meals: return "Which meal? e.g. *how can I improve the burger?*", None, []
        r = df[df["meal"]==meals[0]].iloc[0]; tips=[]
        if r["fiber_g"]<5:         tips.append("add a veg side for more fibre")
        if r["protein_g"]<25:      tips.append("add lean protein (chicken, eggs, legumes)")
        if r["sat_fat_g"]>5:       tips.append("swap fried/fatty items for grilled/steamed")
        if r["calories_kcal"]>700: tips.append("reduce portion size or drop a high-cal item")
        if not tips: tips.append("already a solid meal — maintain this balance")
        return (f"**Improvements for {r['meal']}:**\n" +
                "\n".join(f"• {t}" for t in tips)), None, []
    elif intent == "list":
        return ("**Available meals:**\n" +
                "\n".join(f"{i+1}. {r['meal']} ({r['score']}/100)"
                           for i,(_,r) in enumerate(df.iterrows()))), None, []
    else:
        if meals:
            r = df[df["meal"]==meals[0]].iloc[0]
            return (f"**{r['meal']}** — Score: {r['score']}/100 | "
                    f"{r['calories_kcal']:.0f} kcal | Protein: {r['protein_g']}g | "
                    f"Fibre: {r['fiber_g']}g | Sat.fat: {r['sat_fat_g']}g"), None, []
        return ("I can answer: meal scores, best/worst meals, comparisons, "
                "calories, macros, why a meal scores low, how to improve it."), None, []

# ─── App layout ───────────────────────────────────────────────────────────────
st.title("🥗 Meal NLP Assistant")
st.caption("Ask anything about your meals — powered by real nutrition data")

tab1, tab2, tab3 = st.tabs(["📊 Meal Overview", "💬 Ask the Assistant", "📅 Daily Tracker"])

# ══ TAB 1: Overview ══════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("Meal Quality Scores")
        df_plot = meal_scores.sort_values("score", ascending=True)
        short_labels = [m.replace(" + ", "\n+ ") for m in df_plot["meal"]]
        score_colours = ["#f04438" if s < 25 else "#ffd400" if s < 50
                         else "#17b26a" if s < 75 else "#A1C9F4"
                         for s in df_plot["score"]]
        fig_scores, ax = plt.subplots(figsize=(6, 4))
        fig_scores.patch.set_facecolor("#1D1D20")
        ax.set_facecolor("#1D1D20")
        bars = ax.barh(range(len(df_plot)), df_plot["score"], color=score_colours, height=0.55)
        ax.set_yticks(range(len(df_plot)))
        ax.set_yticklabels([m.split("+")[0].strip() for m in df_plot["meal"]],
                           color="#fbfbff", fontsize=9)
        for bar_, score in zip(bars, df_plot["score"]):
            ax.text(bar_.get_width()+0.5, bar_.get_y()+bar_.get_height()/2,
                    f"{score}", va="center", color="#fbfbff", fontsize=8.5)
        ax.set_xlim(0, 115); ax.set_xlabel("Score / 100", color="#909094", fontsize=9)
        ax.tick_params(colors="#fbfbff")
        for spine in ax.spines.values(): spine.set_visible(False)
        plt.tight_layout()
        st.pyplot(fig_scores)
        plt.close(fig_scores)

    with col_right:
        st.subheader("Macro Breakdown")
        display_cols = ["meal","calories_kcal","protein_g","fiber_g","sat_fat_g","carbs_g"]
        display_df = meal_scores[display_cols].rename(columns={
            "meal":"Meal","calories_kcal":"Kcal","protein_g":"Protein (g)",
            "fiber_g":"Fibre (g)","sat_fat_g":"Sat.Fat (g)","carbs_g":"Carbs (g)"})
        display_df["Meal"] = display_df["Meal"].str.replace(r"^[^\w]+","",regex=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══ TAB 2: NLP Assistant ═════════════════════════════════════════════════════
with tab2:
    col_q, col_a = st.columns([1, 1])
    with col_q:
        st.subheader("💬 Ask a question")
        example_qs = [
            "What is the healthiest meal?",
            "Why is the burger bad?",
            "How much protein does each meal have?",
            "Compare chicken vs oatmeal",
            "How many calories am I eating?",
            "How can I improve the bread meal?",
            "Which meal has the most fibre?",
            "What are the worst meals to eat?",
        ]
        chosen = st.selectbox("Pick an example:", ["— type your own below —"] + example_qs)
        user_q = st.text_input("Or type your question:", value="" if chosen.startswith("—") else chosen)
        if st.button("Ask 🤖", key="ask_btn") and user_q.strip():
            st.session_state["last_answer"] = ask(user_q.strip())

    with col_a:
        st.subheader("🤖 Answer")
        if "last_answer" in st.session_state:
            ans_text, ans_type, ans_meals = st.session_state["last_answer"]
            st.markdown(ans_text)
            if ans_type == "calorie":
                render_calorie_visual(ans_meals)

    st.divider()
    st.subheader("📋 All meals at a glance")
    for _, row in meal_scores.iterrows():
        with st.expander(f"{row['meal']}  —  {row['band']}  ({row['score']}/100)"):
            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("Calories", f"{row['calories_kcal']:.0f} kcal")
            m2.metric("Protein",  f"{row['protein_g']}g")
            m3.metric("Fibre",    f"{row['fiber_g']}g")
            m4.metric("Sat.Fat",  f"{row['sat_fat_g']}g")
            m5.metric("Carbs",    f"{row['carbs_g']}g")

# ══ TAB 3: Daily Tracker ═════════════════════════════════════════════════════
with tab3:
    st.subheader("📅 Daily Calorie Tracker")
    st.caption(f"Select what you ate at each meal slot — tracks against your {DAILY_TARGET} kcal daily goal")

    slots = ["Breakfast", "Lunch", "Dinner", "Snack"]
    slot_defaults = {
        "Breakfast": "🥣 Oatmeal + Banana + Milk",
        "Lunch":     "🍗 Grilled Chicken + Rice + Broccoli",
        "Dinner":    None,
        "Snack":     None,
    }
    SLOT_ICONS = {"Breakfast":"🌅","Lunch":"☀️","Dinner":"🌙","Snack":"🍎"}

    sel_cols = st.columns(4)
    slot_meals = {}
    for i, slot in enumerate(slots):
        with sel_cols[i]:
            options = ["— skip —"] + MEAL_NAMES
            default_idx = (MEAL_NAMES.index(slot_defaults[slot]) + 1
                           if slot_defaults[slot] else 0)
            chosen_meal = st.selectbox(
                f"{SLOT_ICONS[slot]} {slot}",
                options,
                index=default_idx,
                key=f"slot_{slot}"
            )
            slot_meals[slot] = None if chosen_meal == "— skip —" else chosen_meal

    st.divider()
    render_daily_tracker(slot_meals)

    # ── Per-slot breakdown ────────────────────────────────────────────────────
    active = {s: m for s, m in slot_meals.items() if m}
    if active:
        st.subheader("Per-slot details")
        for slot, meal in active.items():
            macros = get_macros(meal)
            with st.expander(f"{SLOT_ICONS[slot]} {slot}: {meal}  ({macros['calories_kcal']:.0f} kcal)"):
                d1,d2,d3,d4 = st.columns(4)
                d1.metric("Calories", f"{macros['calories_kcal']:.0f} kcal")
                d2.metric("Protein",  f"{macros['protein_g']:.1f}g")
                d3.metric("Fibre",    f"{macros['fiber_g']:.1f}g")
                d4.metric("Sat.Fat",  f"{macros['sat_fat_g']:.1f}g")
