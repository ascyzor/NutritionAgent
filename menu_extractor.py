import base64
import json
from typing import Any, Dict, List, Union, cast
import openai
from openai.types.chat import ChatCompletionUserMessageParam
from config import OPENAI_API_KEY, DEBUG_MODE

openai.api_key = OPENAI_API_KEY


def encode_image_to_base64(image_file: Any) -> str:
    """Convert uploaded image to base64 string"""
    return base64.b64encode(image_file.read()).decode('utf-8')


def extract_menu_from_image(image_file: Union[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract dish names and descriptions from menu photo using GPT-4 Vision

    Args:
        image_file: Uploaded image file (Streamlit UploadedFile or file path)

    Returns:
        list: Array of dishes with name, description, and price
    """
    content: str = ""  # Initialize to avoid "might be referenced before assignment" warning
    try:
        # Handle both file path and uploaded file
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
        else:
            base64_image = encode_image_to_base64(image_file)

        prompt = """Analyze this restaurant menu and extract all dishes.

For each dish, provide:
1. **name**: The exact dish name
2. **description**: Ingredients or preparation method (if mentioned)
3. **price**: Price if visible (format: "$X.XX" or null)
4. **category**: appetizer, main, side, dessert, beverage, or other

IMPORTANT RULES:
- Extract EVERY dish you can see, even if partially visible
- If description is unclear, write "No description provided"
- Be precise with dish names (don't add words)
- Include section headers if they help categorize

Return ONLY valid JSON array with no markdown, no preamble:
[
    {
        "name": "Grilled Salmon",
        "description": "Atlantic salmon with roasted vegetables and lemon butter",
        "price": "$24.99",
        "category": "main"
    },
    {
        "name": "Caesar Salad",
        "description": "Romaine lettuce, parmesan, croutons, Caesar dressing",
        "price": "$12.99",
        "category": "appetizer"
    }
]"""

        messages: List[ChatCompletionUserMessageParam] = cast(List[ChatCompletionUserMessageParam], cast(object, [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]))

        response = openai.chat.completions.create(
            model="gpt-5",
            messages=messages,
            max_tokens=2000,
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        if DEBUG_MODE:
            print(f"Raw Vision Response:\\n{content}")

        # Clean up response (remove markdown if present)
        if content.startswith('\`\`\`'):
            content = content.split('\`\`\`')[1]
            if content.startswith('json'):
                content = content[4:]

        dishes = json.loads(content.strip())

        if DEBUG_MODE:
            print(f"Extracted {len(dishes)} dishes")

        return dishes

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Content: {content}")
        return []
    except Exception as e:
        print(f"Vision extraction error: {e}")
        return []


def validate_extracted_dishes(dishes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and clean extracted dish data"""
    validated: List[Dict[str, Any]] = []

    for dish in dishes:
        if 'name' in dish and dish['name']:
            validated.append({
                'name': dish['name'].strip(),
                'description': dish.get('description', 'No description').strip(),
                'price': dish.get('price', 'N/A'),
                'category': dish.get('category', 'other').lower()
            })

    return validated