#  AI Nutrition Agent: Menu Analyzer & Diet Assistant


An **Agentic AI System** that transforms unstructured restaurant menu images into personalized, health-conscious recommendations.

---

## Key Features

*  Multimodal Perception: Digitizes complex or handwritten menus using Vision LLMs.
*  Personalization Engine: Automatically filters menu items based on user health profiles (e.g., Vegan, Keto, Diabetic-friendly).
*  Data Integration: Designed to interface with Public Nutrition Databases (Government APIs) for real-time calorie and macronutrient tracking.
*  Agent Workflow: Uses a reasoning-based approach (Think-Act-Observe) to ensure recommendations are logical and safe.

---

##  Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **AI Model** | OpenAI GPT-4o-mini (Vision & Reasoning) |
| **Framework** | Streamlit (Interactive UI) |
| **Agent Logic** | Built-in Agentic Workflow with Prompt Engineering |
| **Data Handling** | Pydantic & JSON |

---

##  System Architecture

1.  **Input:** User uploads an image of a menu and defines their dietary constraints.
2.  **Analysis:** The Vision model extracts menu items and descriptions.
3.  **Augmentation:** The Agent fetches nutritional data for the detected items.
4.  **Reasoning:** The system evaluates each dish against the user's profile.
5.  **Output:** A curated selection of dishes with nutritional breakdowns and reasoning.

---
