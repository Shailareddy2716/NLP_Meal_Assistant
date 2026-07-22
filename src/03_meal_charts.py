import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BG   = "#1D1D20"
TEXT = "#fbfbff"

def bar_colour(score):
    if score >= 75: return "#8DE5A1"
    if score >= 50: return "#A1C9F4"
    if score >= 25: return "#FFB482"
    return "#FF9F9B"

def plot_scores(meal_scores):
    df = meal_scores.sort_values("score")
    colours = [bar_colour(s) for s in df["score"]]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    bars = ax.barh(df["meal"], df["score"], color=colours, height=0.55)
    for bar, score in zip(bars, df["score"]):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{score}", va="center", ha="left", color=TEXT, fontsize=10, fontweight="bold")
    ax.set_xlim(0, 115)
    ax.set_xlabel("Score (0-100)", color=TEXT)
    ax.set_title("Meal Quality Scores", color=TEXT, fontsize=13, fontweight="bold")
    ax.tick_params(colors=TEXT)
    plt.tight_layout()
    return fig

print("Meal charts module loaded. Call plot_scores(meal_scores).")
