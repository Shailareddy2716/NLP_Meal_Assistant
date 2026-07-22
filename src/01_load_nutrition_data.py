import pandas as pd
import requests
import io

URL = "https://raw.githubusercontent.com/prasertcbs/basic-dataset/master/nutrients.csv"

resp = requests.get(URL, timeout=15)
resp.raise_for_status()

nutrition_raw = pd.read_csv(io.StringIO(resp.text))
nutrition_raw.columns = nutrition_raw.columns.str.strip().str.lower().str.replace(" ", "_")

for col in ["grams", "calories", "protein", "fat", "sat.fat", "fiber", "carbs"]:
    nutrition_raw[col] = pd.to_numeric(
        nutrition_raw[col].astype(str).str.replace(",", ""), errors="coerce"
    )

for col in ["calories", "protein", "fat", "sat.fat", "fiber", "carbs"]:
    nutrition_raw[f"{col}_per100g"] = (nutrition_raw[col] / nutrition_raw["grams"] * 100).round(2)

nutrition_db = nutrition_raw.dropna(subset=["calories_per100g"]).copy()
nutrition_db["food_lower"] = nutrition_db["food"].str.lower().str.strip()

print(f"Loaded {len(nutrition_db)} food items across {nutrition_db['category'].nunique()} categories")
