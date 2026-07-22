# Demo: run sample queries against the NLP assistant
# In Zerve the ask() function is available from the NLP Assistant block.
# Standalone usage: import ask from 05_nlp_assistant and pass a meal_scores DataFrame.

DEMO_QUESTIONS = [
    "What meals are available?",
    "What is the healthiest meal?",
    "What is the worst meal I can eat?",
    "Show me the scores for all meals",
    "Compare chicken vs burger",
    "Why is the burger rated so poorly?",
    "How much protein does each meal have?",
    "How many calories are in the oatmeal?",
    "How can I improve the bread meal?",
    "Which meal has the most fibre?",
]

if __name__ == "__main__":
    print("Demo questions:")
    for q in DEMO_QUESTIONS:
        print(f"  - {q}")
