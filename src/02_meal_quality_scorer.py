import pandas as pd
import numpy as np

MEALS = {
    "Grilled Chicken + Rice + Broccoli": [
        ("Chicken, broilers or fryers", 150),
        ("Rice, white, cooked", 120),
        ("Broccoli", 100),
    ],
    "Burger + Chips + Cola": [
        ("Hamburger", 200),
        ("Potato chips", 100),
        ("Cola beverages", 350),
    ],
    "Oatmeal + Banana + Milk": [
        ("Oatmeal", 80),
        ("Banana", 120),
        ("Cows' milk", 200),
    ],
    "White Bread + Butter + Jam": [
        ("White bread", 80),
        ("Butter", 20),
        ("Strawberry jam", 30),
    ],
    "Egg + Spinach + Whole Wheat Toast": [
        ("Eggs raw", 120),
        ("Spinach", 80),
        ("Whole-wheat", 60),
    ],
}

MANUAL_NUTRITION = {
    "Chicken, broilers or fryers": (165, 31.0, 3.6, 1.0, 0.0, 0.0),
    "Rice, white, cooked":          (130,  2.7, 0.3, 0.1, 0.4, 28.0),
    "Cola beverages":               ( 41,  0.0, 0.0, 0.0, 0.0, 10.6),
    "Strawberry jam":               (250,  0.4, 0.1, 0.0, 1.0, 65.0),
    "White bread":                  (265,  9.0, 3.2, 0.7, 2.7, 49.0),
}

def score_meal(m):
    protein  = m["protein_g"]   if not np.isnan(m["protein_g"])   else 0
    fibre    = m["fiber_g"]     if not np.isnan(m["fiber_g"])     else 0
    sat_fat  = m["sat_fat_g"]   if not np.isnan(m["sat_fat_g"])   else 0
    calories = m["calories_kcal"]
    protein_score   = min(protein / 35 * 30, 30)
    fibre_score     = min(fibre   / 8  * 30, 30)
    sat_fat_penalty = min(max(sat_fat  - 5,   0) / 10  * 20, 20)
    calorie_penalty = min(max(calories - 700, 0) / 500 * 20, 20)
    raw = protein_score + fibre_score - sat_fat_penalty - calorie_penalty
    return round(float(max(min(raw, 100), 0)), 1)

print("Meal scorer loaded. Call score_meal(row) with a meal totals dict.")
