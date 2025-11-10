import json
import openai
from config import OPENAI_API_KEY, DEBUG_MODE
from typing import List, cast
from openai.types.chat import ChatCompletionUserMessageParam

openai.api_key = OPENAI_API_KEY


def analyze_menu_with_preferences(dishes_with_nutrition, user_preferences):
    """
    Use LLM agent to analyze menu and provide personalized recommendations

    Args:
        dishes_with_nutrition: List of dishes with nutrition data
        user_preferences: Dict with goal, diet_type, allergies, calorie_target

    Returns:
        dict: Analysis results with rankings, recommendations, and combos
    """

    # Build menu context for LLM
    menu_context = "\n".join([
        f"- {d['dish']}: {d['calories']} cal, "
        f"{d['protein']}g protein, {d['carbs']}g carbs, {d['fat']}g fat"
        + (f", {d.get('description', '')}" if d.get('description') else "")
        for d in dishes_with_nutrition
    ])

    # Build allergy list
    allergies_text = ', '.join(user_preferences.get('allergies', [])) if user_preferences.get('allergies') else 'none'

    prompt = f"""You are an expert nutritionist analyzing a restaurant menu for a specific client.

USER PROFILE:
- Health Goal: {user_preferences['goal'].replace('_', ' ').title()}
- Dietary Preference: {user_preferences['diet_type'].title()}
- Allergies/Restrictions: {allergies_text}
- Target Calories per Meal: {user_preferences['calorie_target']}

MENU OPTIONS:
{menu_context}

YOUR TASKS:
1. **Rank all dishes** from best to worst for this user's specific goals and restrictions
2. **Identify top 3 dishes** with detailed explanations of why they're optimal
3. **Flag dishes to avoid** with specific reasons (allergens, poor nutrition, goal mismatch)
4. **Create 2-3 meal combinations** (appetizer+main or main+side) that:
   - Hit the calorie target (±50 calories)
   - Maximize nutrition for their goal
   - Respect dietary restrictions
5. **List allergen warnings** for any dishes containing their allergens

SCORING CRITERIA:
- Weight Loss: Prioritize protein, fiber, low calories, avoid sugar
- Muscle Gain: Prioritize protein (>30g), moderate calories, good carbs
- Maintain Health: Balance of all macros, avoid excessive sodium/sugar

Return response as VALID JSON ONLY (no markdown, no preamble):
{{
    "ranked_dishes": [
        {{
            "name": "dish name",
            "rank": 1,
            "score": 95,
            "reason": "High protein (35g), moderate calories (450), fits low-carb preference"
        }}
    ],
    "top_picks": [
        {{
            "name": "dish name",
            "why_good": "Perfect macros for muscle gain with 40g protein and complex carbs",
            "nutrition_highlights": "40g protein, 55g carbs, 450 calories",
            "eating_tips": "Ask for extra vegetables instead of rice to lower carbs"
        }}
    ],
    "avoid": [
        {{
            "name": "dish name",
            "reason": "Contains dairy (user allergy) and excessive sugar (45g)"
        }}
    ],
    "meal_combos": [
        {{
            "items": ["Greek Salad", "Grilled Chicken Breast"],
            "total_calories": 580,
            "total_protein": 48,
            "total_carbs": 35,
            "total_fat": 22,
            "why_good": "Protein-rich combo with healthy fats from olive oil, hits calorie target perfectly",
            "cost_estimate": "$28"
        }}
    ],
    "allergen_warnings": [
        "Pasta Alfredo contains dairy",
        "Pecan Pie contains nuts"
    ],
    "general_advice": "Focus on grilled proteins and avoid fried options. Ask for dressings on the side."
}}"""

    content: str = ""
    try:
        messages: List[ChatCompletionUserMessageParam] = cast(List[ChatCompletionUserMessageParam], cast(object, [
            {
                "role": "system",
                "content": "You are a certified nutritionist providing personalized dietary advice. Always prioritize user health and safety."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]))
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=2500
        )

        content = response.choices[0].message.content.strip()

        if DEBUG_MODE:
            print(f"Raw Agent Response:\\n{content}")

        # Clean markdown if present
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]

        analysis = json.loads(content.strip())

        return analysis

    except json.JSONDecodeError as e:
        print(f"Agent JSON parse error: {e}")
        print(f"Content: {content}")
        return get_fallback_analysis(dishes_with_nutrition, user_preferences)
    except Exception as e:
        print(f"Agent analysis error: {e}")
        return get_fallback_analysis(dishes_with_nutrition, user_preferences)


def get_fallback_analysis(dishes, user_prefs):
    """Simple rule-based analysis if LLM fails"""

    # Sort by calories (ascending for weight loss, descending for muscle gain)
    sorted_dishes = sorted(
        dishes,
        key=lambda x: x['calories'],
        reverse=(user_prefs['goal'] == 'muscle_gain')
    )

    return {
        "ranked_dishes": [
            {
                "name": d['name'],
                "rank": i + 1,
                "score": 100 - (i * 5),
                "reason": f"{d['calories']} calories, {d['protein']}g protein"
            }
            for i, d in enumerate(sorted_dishes[:10])
        ],
        "top_picks": [
            {
                "name": sorted_dishes[0]['name'],
                "why_good": "Best match based on calorie and protein content",
                "nutrition_highlights": f"{sorted_dishes[0]['calories']} cal, {sorted_dishes[0]['protein']}g protein"
            }
        ],
        "avoid": [],
        "meal_combos": [],
        "allergen_warnings": [],
        "general_advice": "Analysis based on basic nutrition data. For detailed recommendations, ensure API connection."
    }