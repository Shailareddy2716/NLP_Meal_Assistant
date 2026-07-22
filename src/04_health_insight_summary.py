TIPS = {
    "Grilled Chicken + Rice + Broccoli": (
        "Low fibre (only 1.8g). Swap white rice for brown rice or add lentils/beans."
    ),
    "Egg + Spinach + Whole Wheat Toast": (
        "Sat. fat is high (13.3g). Use 1 whole egg + 2 egg whites, minimal oil."
    ),
    "Oatmeal + Banana + Milk": (
        "Switch to oat milk or semi-skimmed to halve the saturated fat."
    ),
    "White Bread + Butter + Jam": (
        "Low protein and fibre. Add nut butter + wholegrain bread."
    ),
    "Burger + Chips + Cola": (
        "Sat. fat is 35g — nearly 3x daily limit. Swap chips for salad, cola for water."
    ),
}

def print_summary(meal_scores):
    best  = meal_scores.iloc[0]
    worst = meal_scores.iloc[-1]
    print(f"Best  meal: {best['meal']} ({best['score']}/100)")
    print(f"Worst meal: {worst['meal']} ({worst['score']}/100)")
    print("\nTips:")
    for _, row in meal_scores.iterrows():
        tip = TIPS.get(row["meal"], "Add more vegetables for fibre.")
        print(f"  {row['meal']}: {tip}")

print("Health insight summary module loaded.")
