import requests
import time
from config import (
    USDA_API_KEY,
    USDA_SEARCH_URL,
    DEBUG_MODE
)


def get_nutrition_usda(dish_name):
    """
    Fetch nutrition data from USDA FoodData Central (Fallback)

    Args:
        dish_name: Name of the dish

    Returns:
        dict: Nutrition data or None if failed
    """
    if not USDA_API_KEY:
        if DEBUG_MODE:
            print("USDA API key not configured, skipping...")
        return None

    try:
        params = {
            "query": dish_name,
            "dataType": ["Survey (FNDDS)", "Branded"],
            "pageSize": 1,
            "api_key": USDA_API_KEY
        }

        response = requests.get(USDA_SEARCH_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            foods = data.get('foods', [])

            if foods:
                food = foods[0]
                nutrients = {
                    n['nutrientName']: n['value']
                    for n in food.get('foodNutrients', [])
                }

                result = {
                    "dish": dish_name,
                    "calories": round(nutrients.get('Energy', 0)),
                    "protein": round(nutrients.get('Protein', 0), 1),
                    "carbs": round(nutrients.get('Carbohydrate, by difference', 0), 1),
                    "fat": round(nutrients.get('Total lipid (fat)', 0), 1),
                    "fiber": round(nutrients.get('Fiber, total dietary', 0), 1),
                    "sugar": round(nutrients.get('Sugars, total including NLEA', 0), 1),
                    "sodium": round(nutrients.get('Sodium, Na', 0)),
                    "serving_size": 100,
                    "serving_unit": "g",
                    "source": "usda"
                }

                if DEBUG_MODE:
                    print(f"✓ USDA: {dish_name} - {result['calories']} cal")

                return result

        return None

    except Exception as e:
        print(f"USDA error for {dish_name}: {e}")
        return None


def get_nutrition_with_fallback(dish_name, description=""):
    """
    Try multiple nutrition sources with fallback

    Priority: Nutritionix → USDA → GPT Estimation
    """

    # Try USDA first
    result = get_nutrition_usda(dish_name)
    if result:
        return result

    # Last resort: GPT estimation (implement if needed)
    if DEBUG_MODE:
        print(f"⚠ No nutrition data found for: {dish_name}")

    return None


def batch_fetch_nutrition(dishes, max_workers=5):
    """
    Fetch nutrition for multiple dishes with rate limiting

    Args:
        dishes: List of dish dictionaries
        max_workers: Number of concurrent requests (be mindful of rate limits)

    Returns:
        list: Dishes with nutrition data added
    """
    results = []

    for i, dish in enumerate(dishes):
        nutrition = get_nutrition_with_fallback(
            dish['name'],
            dish.get('description', '')
        )

        if nutrition:
            # Merge nutrition data with dish info
            dish_with_nutrition = {**dish, **nutrition}
            results.append(dish_with_nutrition)

        # Rate limiting (Nutritionix free tier: ~3 req/sec)
        if i < len(dishes) - 1:
            time.sleep(0.4)

    return results