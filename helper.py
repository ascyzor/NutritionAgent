def format_price(price_str):
    """Clean and format price strings"""
    if not price_str or price_str == 'N/A':
        return None

    # Remove currency symbols and extra spaces
    import re
    cleaned = re.sub(r'[^0-9.]', '', str(price_str))
    try:
        return float(cleaned)
    except:
        return None


def calculate_macro_percentages(calories, protein, carbs, fat):
    """Calculate macronutrient percentages"""
    total_cals_from_macros = (protein * 4) + (carbs * 4) + (fat * 9)

    if total_cals_from_macros == 0:
        return {"protein": 0, "carbs": 0, "fat": 0}

    return {
        "protein": round((protein * 4 / total_cals_from_macros) * 100),
        "carbs": round((carbs * 4 / total_cals_from_macros) * 100),
        "fat": round((fat * 9 / total_cals_from_macros) * 100)
    }


def health_score(dish, goal="maintain_health"):
    """
    Calculate simple health score (0-100) for a dish
    Higher protein, lower sugar = better for most goals
    """
    score = 50  # Base score

    # Protein bonus
    if dish.get('protein', 0) > 30:
        score += 20
    elif dish.get('protein', 0) > 20:
        score += 10

    # Calorie penalty (for weight loss)
    if goal == "weight_loss":
        if dish.get('calories', 0) < 400:
            score += 15
        elif dish.get('calories', 0) > 700:
            score -= 15

    # Sugar penalty
    if dish.get('sugar', 0) > 20:
        score -= 20

    # Fiber bonus
    if dish.get('fiber', 0) > 5:
        score += 10

    return max(0, min(100, score))


def check_allergens(dish_name, description, allergen_list):
    """
    Simple allergen detection in dish name/description
    Returns list of detected allergens
    """
    detected = []
    text = f"{dish_name} {description}".lower()

    allergen_keywords = {
        "nuts": ["nut", "almond", "walnut", "pecan", "cashew", "peanut"],
        "dairy": ["milk", "cheese", "cream", "butter", "yogurt"],
        "gluten": ["wheat", "bread", "pasta", "flour"],
        "shellfish": ["shrimp", "crab", "lobster", "oyster"],
        "eggs": ["egg"],
        "soy": ["soy", "tofu", "edamame"]
    }

    for allergen in allergen_list:
        keywords = allergen_keywords.get(allergen.lower(), [])
        if any(keyword in text for keyword in keywords):
            detected.append(allergen)

    return detected