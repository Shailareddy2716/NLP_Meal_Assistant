
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re

st.set_page_config(page_title="🥗 Meal NLP Assistant", layout="wide", page_icon="🥗")

# ─── Dark theme for Plotly ────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#1D1D20", plot_bgcolor="#1D1D20",
    font=dict(color="#fbfbff", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
)

# ─── Nutrition data ───────────────────────────────────────────────────────────
MANUAL_NUTRITION = {
    "chicken":       (165, 31.0, 3.6,  1.0, 0.0,  0.0),
    "rice":          (130,  2.7, 0.3,  0.1, 0.4, 28.0),
    "cola":          ( 41,  0.0, 0.0,  0.0, 0.0, 10.6),
    "jam":           (250,  0.4, 0.1,  0.0, 1.0, 65.0),
    "white bread":   (265,  9.0, 3.2,  0.7, 2.7, 49.0),
    "broccoli":      ( 34,  2.8, 0.4,  0.0, 2.6,  6.6),
    "burger":        (295, 17.0,17.0,  6.5, 0.5, 24.0),
    "chips":         (536,  7.0,35.0,  3.5, 4.4, 53.0),
    "oatmeal":       (371, 13.0, 6.5,  1.2,10.0, 67.0),
    "banana":        ( 89,  1.1, 0.3,  0.1, 2.6, 23.0),
    "milk":          ( 61,  3.2, 3.3,  2.1, 0.0,  4.8),
    "butter":        (717,  0.9,81.0, 51.4, 0.0,  0.1),
    "egg":           (143, 12.6, 9.5,  3.1, 0.0,  0.7),
    "eggs":          (143, 12.6, 9.5,  3.1, 0.0,  0.7),
    "spinach":       ( 23,  2.9, 0.4,  0.1, 2.2,  3.6),
    "wheat bread":   (247,  9.4, 3.4,  0.7, 6.0, 48.0),
    "whole wheat":   (247,  9.4, 3.4,  0.7, 6.0, 48.0),
    "toast":         (265,  9.0, 3.2,  0.7, 2.7, 49.0),
    "salmon":        (208, 20.0,13.0,  3.1, 0.0,  0.0),
    "tuna":          (132, 29.0, 1.3,  0.3, 0.0,  0.0),
    "apple":         ( 52,  0.3, 0.2,  0.0, 2.4, 14.0),
    "yogurt":        ( 59,  3.5, 3.3,  2.1, 0.0,  4.7),
    "pasta":         (158,  5.8, 0.9,  0.2, 1.8, 31.0),
    "potato":        ( 77,  2.0, 0.1,  0.0, 1.8, 17.0),
    "cheese":        (402, 25.0,33.0, 21.0, 0.0,  1.3),
    "bread":         (265,  9.0, 3.2,  0.7, 2.7, 49.0),
    "beef":          (250, 26.0,17.0,  6.5, 0.0,  0.0),
    "pork":          (242, 27.0,14.0,  5.1, 0.0,  0.0),
    "carrot":        ( 41,  0.9, 0.2,  0.0, 2.8,  9.6),
    "lettuce":       ( 15,  1.4, 0.2,  0.0, 1.3,  2.9),
    "tomato":        ( 18,  0.9, 0.2,  0.0, 1.2,  3.9),
    "cucumber":      ( 16,  0.7, 0.1,  0.0, 0.5,  3.6),
    "orange":        ( 47,  0.9, 0.1,  0.0, 2.4, 12.0),
    "strawberry":    ( 32,  0.7, 0.3,  0.0, 2.0,  7.7),
    "almond":        (579, 21.0,50.0,  3.8,12.5, 22.0),
    "peanut butter": (588, 25.0,50.0,  9.0, 6.0, 20.0),
}

PRESET_MEALS = {
    "🍗 Grilled Chicken + Rice + Broccoli": [("chicken",150),("rice",120),("broccoli",100)],
    "🍔 Burger + Chips + Cola":             [("burger",200),("chips",100),("cola",350)],
    "🥣 Oatmeal + Banana + Milk":           [("oatmeal",80),("banana",120),("milk",200)],
    "🍞 White Bread + Butter + Jam":        [("white bread",80),("butter",20),("jam",30)],
    "🥚 Egg + Spinach + Whole Wheat Toast": [("egg",120),("spinach",80),("wheat bread",60)],
}

DAILY_TARGET = 2000

# ─── Macro helpers ────────────────────────────────────────────────────────────
def parse_macros_from_ingredients(ingredients):
    totals = dict(calories_kcal=0.0, protein_g=0.0, fat_g=0.0,
                  sat_fat_g=0.0, fiber_g=0.0, carbs_g=0.0)
    for food, grams in ingredients:
        if food in MANUAL_NUTRITION:
            c,p,f,sf,fi,cb = MANUAL_NUTRITION[food]
            s = grams / 100
            totals["calories_kcal"] += c*s; totals["protein_g"] += p*s
            totals["fat_g"]         += f*s; totals["sat_fat_g"] += sf*s
            totals["fiber_g"]       += fi*s; totals["carbs_g"]  += cb*s
    return {k: round(v,1) for k,v in totals.items()}

def macros_for_preset(meal_name):
    return parse_macros_from_ingredients(PRESET_MEALS[meal_name])

def score_macros(m):
    s = (min(m["protein_g"]/35*30,30) + min(m["fiber_g"]/8*30,30)
         - min(max(m["sat_fat_g"]-5,0)/10*20,20)
         - min(max(m["calories_kcal"]-700,0)/500*20,20))
    return round(float(max(min(s,100),0)),1)

@st.cache_data
def build_meal_scores():
    rows = []
    for name, ingr in PRESET_MEALS.items():
        m = parse_macros_from_ingredients(ingr)
        score = score_macros(m)
        band = ("🔴 Poor" if score<25 else "🟡 Okay" if score<50
                else "🟢 Good" if score<75 else "🌟 Excellent")
        rows.append({"meal":name,"score":score,"band":band,**m})
    return pd.DataFrame(rows).sort_values("score",ascending=False).reset_index(drop=True)

meal_scores = build_meal_scores()

# ─── Custom meal parser ───────────────────────────────────────────────────────
def parse_custom_meal(text):
    """Parse '200g chicken, 100g rice' → list of (food, grams), unmatched list."""
    pattern = re.compile(r"(\d+)\s*g\s+([a-z ]+?)(?=,|$|\d)", re.IGNORECASE)
    matched, unmatched = [], []
    for m in pattern.finditer(text):
        grams = int(m.group(1))
        food  = m.group(2).strip().lower()
        best  = next((k for k in MANUAL_NUTRITION if food in k or k in food), None)
        if best:
            matched.append((best, grams))
        else:
            unmatched.append(food)
    return matched, unmatched

# ─── Plotly chart functions ───────────────────────────────────────────────────
def calorie_bar_chart(meals_list, title="Calorie Comparison"):
    df = meal_scores[meal_scores["meal"].isin(meals_list)].sort_values("calories_kcal")
    colours = ["#17b26a" if k<=700*0.75 else "#ffd400" if k<=700 else "#f04438"
               for k in df["calories_kcal"]]
    short = [m.split("+")[0].strip()[:20] for m in df["meal"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=short, x=df["calories_kcal"], orientation="h",
        marker_color=colours, text=[f"{k:.0f} kcal" for k in df["calories_kcal"]],
        textposition="outside", hovertemplate="%{y}<br><b>%{x:.0f} kcal</b><extra></extra>",
    ))
    fig.add_vline(x=700, line_dash="dash", line_color="#fbfbff", opacity=0.5,
                  annotation_text="700 kcal target", annotation_font_color="#909094")
    fig.update_layout(**PLOTLY_LAYOUT, title=title,
                      xaxis_title="Calories (kcal)", height=max(200, 60*len(df)))
    return fig

def macro_radar_chart(meal_name, title=None):
    row = meal_scores[meal_scores["meal"]==meal_name].iloc[0]
    cats   = ["Protein (g)","Fat (g)","Fibre (g)","Carbs (g)","Sat.Fat (g)"]
    vals   = [row["protein_g"],row["fat_g"],row["fiber_g"],row["carbs_g"],row["sat_fat_g"]]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(161,201,244,0.3)",
        line=dict(color="#A1C9F4", width=2),
        hovertemplate="%{theta}: <b>%{r:.1f}</b><extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT,
                      title=title or f"Macro Profile — {meal_name.split('+')[0].strip()}",
                      polar=dict(
                          bgcolor="#2a2a2e",
                          radialaxis=dict(visible=True, color="#909094", gridcolor="#444"),
                          angularaxis=dict(color="#fbfbff", gridcolor="#444"),
                      ), height=350)
    return fig

def compare_bar_chart(meal_a, meal_b):
    cols = ["calories_kcal","protein_g","fiber_g","fat_g","sat_fat_g"]
    labels = ["Calories","Protein","Fibre","Fat","Sat.Fat"]
    ra = meal_scores[meal_scores["meal"]==meal_a].iloc[0]
    rb = meal_scores[meal_scores["meal"]==meal_b].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=meal_a.split("+")[0].strip()[:18],
                         x=labels, y=[ra[c] for c in cols],
                         marker_color="#A1C9F4",
                         hovertemplate="%{x}: <b>%{y:.1f}</b><extra></extra>"))
    fig.add_trace(go.Bar(name=meal_b.split("+")[0].strip()[:18],
                         x=labels, y=[rb[c] for c in cols],
                         marker_color="#FFB482",
                         hovertemplate="%{x}: <b>%{y:.1f}</b><extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT, title="Meal Comparison",
                      barmode="group", height=350)
    return fig

def ranked_score_chart():
    df = meal_scores.sort_values("score")
    colours = ["#f04438" if s<25 else "#ffd400" if s<50 else "#8DE5A1" if s<75 else "#17b26a"
               for s in df["score"]]
    short = [m.split("+")[0].strip()[:20] for m in df["meal"]]
    fig = go.Figure(go.Bar(
        y=short, x=df["score"], orientation="h",
        marker_color=colours,
        text=[f"{s}/100" for s in df["score"]], textposition="outside",
        hovertemplate="%{y}<br><b>Score: %{x}/100</b><extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Meal Quality Rankings",
                      xaxis_title="Health Score (0–100)", xaxis_range=[0,120], height=300)
    return fig

def daily_stacked_chart(slot_data):
    SLOT_COLOURS = {"Breakfast":"#A1C9F4","Lunch":"#8DE5A1","Dinner":"#FFB482","Snack":"#D0BBFF","Custom":"#FF9F9B"}
    fig = go.Figure()
    total = sum(d["calories_kcal"] for d in slot_data.values())
    for slot, macros in slot_data.items():
        kcal = macros["calories_kcal"]
        fig.add_trace(go.Bar(
            name=f"{slot} ({kcal:.0f} kcal)",
            x=[kcal], y=["Daily total"], orientation="h",
            marker_color=SLOT_COLOURS.get(slot,"#fbfbff"),
            hovertemplate=f"<b>{slot}</b><br>{kcal:.0f} kcal<br>Protein: {macros['protein_g']:.1f}g<br>Fibre: {macros['fiber_g']:.1f}g<extra></extra>",
        ))
    fig.add_vline(x=DAILY_TARGET, line_dash="dash", line_color="#fbfbff", opacity=0.6,
                  annotation_text="2000 kcal goal", annotation_font_color="#909094")
    fig.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=180,
                      title=f"Running Total: {total:.0f} / {DAILY_TARGET} kcal",
                      xaxis_range=[0, max(DAILY_TARGET*1.3, total*1.1)])
    return fig

# ─── NLP engine ───────────────────────────────────────────────────────────────
INTENT_MAP = {
    "calorie": ["calories","calorie","kcal","energy","how much am i eating","how many calories","caloric"],
    "compare": ["vs","versus","compare","better","healthier","difference","between"],
    "best":    ["best","healthiest","top","recommend","should i eat","what to eat"],
    "worst":   ["worst","unhealthiest","bad","avoid"],
    "score":   ["score","rating","rate","ranked","rank","quality","how good","points"],
    "macro":   ["protein","fibre","fiber","fat","carbs","saturated","macro","nutrition","nutrient"],
    "why":     ["why","reason","explain","because"],
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

def detect_intent(q):
    q = q.lower()
    for intent, kws in INTENT_MAP.items():
        if any(k in q for k in kws):
            return intent
    return "list"

def detect_meals(q):
    q = q.lower()
    found = list(dict.fromkeys(v for k,v in MEAL_ALIASES.items() if k in q))
    return found if found else list(PRESET_MEALS.keys())

def nlp_answer(question):
    intent = detect_intent(question)
    meals  = detect_meals(question)
    ms     = meal_scores

    if intent == "list":
        txt = "**Available meals:**\n" + "\n".join(
            f"- {r['meal']} — {r['score']}/100" for _,r in ms.iterrows())
        return txt, None

    if intent == "best":
        r = ms.iloc[0]
        return (f"✅ **Healthiest meal:** {r['meal']}\n"
                f"Score: **{r['score']}/100** | {r['calories_kcal']:.0f} kcal | "
                f"Protein: {r['protein_g']:.1f}g"), ranked_score_chart()

    if intent == "worst":
        r = ms.iloc[-1]
        return (f"❌ **Least healthy:** {r['meal']}\n"
                f"Score: **{r['score']}/100** | {r['calories_kcal']:.0f} kcal | "
                f"Sat.Fat: {r['sat_fat_g']:.1f}g"), ranked_score_chart()

    if intent == "score":
        m = meals[0]
        r = ms[ms["meal"]==m].iloc[0]
        return (f"**{r['meal']}**\nScore: **{r['score']}/100** ({r['band']})"), ranked_score_chart()

    if intent == "calorie":
        target = meals if len(meals)<5 else list(PRESET_MEALS.keys())
        df = ms[ms["meal"].isin(target)].sort_values("calories_kcal",ascending=False)
        txt = "**Calories per meal:**\n" + "\n".join(
            f"- {r['meal'].split('+')[0].strip()}: **{r['calories_kcal']:.0f} kcal**"
            for _,r in df.iterrows())
        return txt, calorie_bar_chart(target, "Calories in Your Meals")

    if intent == "compare" and len(meals)>=2:
        a,b = meals[0],meals[1]
        ra = ms[ms["meal"]==a].iloc[0]; rb = ms[ms["meal"]==b].iloc[0]
        winner = a if ra["score"]>rb["score"] else b
        return (f"**{winner.split('+')[0].strip()}** wins by "
                f"{abs(ra['score']-rb['score']):.1f} pts"), compare_bar_chart(a,b)

    if intent == "macro":
        m = meals[0]
        r = ms[ms["meal"]==m].iloc[0]
        return (f"**{r['meal']}** macros:\n"
                f"Protein: {r['protein_g']:.1f}g | Fat: {r['fat_g']:.1f}g | "
                f"Fibre: {r['fiber_g']:.1f}g | Carbs: {r['carbs_g']:.1f}g"), macro_radar_chart(m)

    if intent == "why":
        m = meals[0]; r = ms[ms["meal"]==m].iloc[0]
        issues = []
        if r["protein_g"]<20: issues.append("low protein")
        if r["fiber_g"]<5:    issues.append("low fibre")
        if r["sat_fat_g"]>5:  issues.append("high saturated fat")
        if r["calories_kcal"]>700: issues.append("high calories")
        return (f"**{r['meal']}** scores {r['score']}/100 because: "
                + (", ".join(issues) if issues else "it's balanced!")), macro_radar_chart(m)

    if intent == "improve":
        m = meals[0]; r = ms[ms["meal"]==m].iloc[0]
        tips = []
        if r["protein_g"]<25: tips.append("add lean protein (chicken/egg)")
        if r["fiber_g"]<6:    tips.append("add vegetables for fibre")
        if r["sat_fat_g"]>5:  tips.append("reduce butter/cheese")
        if r["calories_kcal"]>700: tips.append("reduce portion size")
        return "💡 **Tips:** " + "; ".join(tips if tips else ["Meal is already well-balanced!"]), None

    return "Ask me about calories, health scores, macros, or how to improve a meal!", None

# ─── Streamlit UI ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, .stApp { background-color: #1D1D20; color: #fbfbff; }
.stTabs [data-baseweb="tab"] { color: #909094; }
.stTabs [aria-selected="true"] { color: #fbfbff; border-bottom: 2px solid #A1C9F4; }
.meal-card { background:#2a2a2e; border-radius:10px; padding:12px 16px; margin:6px 0; }
.running-total { font-size:2rem; font-weight:800; color:#ffd400; }
</style>""", unsafe_allow_html=True)

st.title("🥗 Meal NLP Assistant")
st.caption("Ask questions about your meals · Track daily calories live · Add custom foods")

tab1, tab2, tab3 = st.tabs(["🤖 NLP Assistant", "📅 Daily Tracker", "🍽️ Meal Scores"])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — NLP Assistant with instant visuals
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Ask anything about your meals")
    with st.expander("💡 Example questions"):
        st.markdown("""
- How many calories am I eating?
- What is the healthiest meal?
- Compare chicken vs burger
- How much protein does the egg meal have?
- Why is the burger bad?
- How can I improve the bread meal?
        """)

    question = st.text_input("", placeholder="Type your question here…", key="nlp_q",
                             label_visibility="collapsed")
    if question.strip():
        answer_txt, chart = nlp_answer(question)
        col_a, col_b = st.columns([1,1]) if chart else (st, None)
        with (col_a if chart else st):
            st.markdown(f"**🤖 Answer:**\n\n{answer_txt}")
        if chart:
            with col_b:
                st.plotly_chart(chart, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Dynamic Daily Tracker
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Daily Calorie Tracker")
    st.caption("Add meals one by one — total updates instantly with each addition")

    if "tracker_slots" not in st.session_state:
        st.session_state.tracker_slots = {}   # {label: macros_dict}

    # ── Add a meal ──────────────────────────────────────────────
    with st.container():
        st.markdown("#### ➕ Add a meal")
        mode = st.radio("Input method", ["Pick a preset meal", "Type custom ingredients"],
                        horizontal=True, label_visibility="collapsed")

        add_col1, add_col2, add_col3 = st.columns([1.5, 2, 1])
        with add_col1:
            slot_label = st.selectbox("Meal slot", ["Breakfast","Lunch","Dinner","Snack","Custom"], key="slot")
        with add_col2:
            if mode == "Pick a preset meal":
                picked = st.selectbox("Choose meal", list(PRESET_MEALS.keys()), key="preset_pick")
                custom_text = None
            else:
                custom_text = st.text_input("e.g. 200g chicken, 100g rice, 80g spinach",
                                            key="custom_text", label_visibility="collapsed",
                                            placeholder="200g chicken, 100g rice, 80g spinach")
                picked = None
        with add_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            add_btn = st.button("➕ Add", use_container_width=True)

        if add_btn:
            if mode == "Pick a preset meal":
                macros = macros_for_preset(picked)
                label  = f"{slot_label}: {picked.split('+')[0].strip()[:20]}"
                st.session_state.tracker_slots[label] = macros
                st.success(f"Added {picked.split('+')[0].strip()} → {macros['calories_kcal']:.0f} kcal")
            elif custom_text and custom_text.strip():
                matched, unmatched = parse_custom_meal(custom_text)
                if matched:
                    macros = parse_macros_from_ingredients(matched)
                    label  = f"{slot_label}: Custom ({', '.join(f[0] for f in matched[:2])}…)"
                    st.session_state.tracker_slots[label] = macros
                    st.success(f"Added custom meal → {macros['calories_kcal']:.0f} kcal")
                    if unmatched:
                        st.warning(f"Couldn't find: {', '.join(unmatched)} — skipped")
                else:
                    st.error("No foods matched. Try: '200g chicken, 100g rice'")

    st.divider()

    # ── Running total ───────────────────────────────────────────
    slots = st.session_state.tracker_slots
    if slots:
        total_kcal    = sum(m["calories_kcal"] for m in slots.values())
        total_protein = sum(m["protein_g"]     for m in slots.values())
        total_fibre   = sum(m["fiber_g"]       for m in slots.values())
        pct = min(total_kcal/DAILY_TARGET*100, 150)

        # Big running total number
        colour = "#17b26a" if total_kcal<=DAILY_TARGET*0.75 else "#ffd400" if total_kcal<=DAILY_TARGET else "#f04438"
        st.markdown(
            f'<div style="text-align:center">'
            f'<span class="running-total" style="color:{colour}">{total_kcal:.0f}</span>'
            f' <span style="color:#909094;font-size:1.2rem">/ {DAILY_TARGET} kcal today</span>'
            f'</div>', unsafe_allow_html=True)

        # Live stacked bar (updates per add)
        st.plotly_chart(daily_stacked_chart(slots), use_container_width=True)

        # Macro tiles
        m1,m2,m3 = st.columns(3)
        m1.metric("💪 Protein", f"{total_protein:.1f}g",
                  delta="✅ on track" if total_protein>=100 else f"{100-total_protein:.0f}g to go")
        m2.metric("🌿 Fibre",   f"{total_fibre:.1f}g",
                  delta="✅ on track" if total_fibre>=25 else f"{25-total_fibre:.0f}g to go")
        m3.metric("🔥 Calories", f"{total_kcal:.0f}",
                  delta=f"{total_kcal-DAILY_TARGET:+.0f} vs 2000 goal")

        st.divider()
        st.markdown("#### 📋 Meals added today")
        for label, macros in slots.items():
            st.markdown(
                f'<div class="meal-card">🍽️ <b>{label}</b> &nbsp;|&nbsp; '
                f'{macros["calories_kcal"]:.0f} kcal &nbsp;|&nbsp; '
                f'P: {macros["protein_g"]:.1f}g &nbsp;|&nbsp; '
                f'F: {macros["fiber_g"]:.1f}g fibre</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear all meals"):
            st.session_state.tracker_slots = {}
            st.rerun()
    else:
        st.info("No meals added yet — use the form above to start tracking.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Meal Scores overview
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("All Meal Quality Scores")
    st.plotly_chart(ranked_score_chart(), use_container_width=True)
    st.subheader("Macro Profiles")
    sel = st.selectbox("Select a meal to see its macro radar", list(PRESET_MEALS.keys()))
    st.plotly_chart(macro_radar_chart(sel), use_container_width=True)
    st.dataframe(
        meal_scores[["meal","score","band","calories_kcal","protein_g","fiber_g","sat_fat_g","carbs_g"]]
        .rename(columns={"calories_kcal":"kcal","protein_g":"protein","fiber_g":"fibre",
                         "sat_fat_g":"sat.fat","carbs_g":"carbs"}),
        use_container_width=True, hide_index=True,
    )
