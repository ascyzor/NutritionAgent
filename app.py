import streamlit as st
import json
from PIL import Image

# Import our custom modules
from menu_extractor import extract_menu_from_image, validate_extracted_dishes
from nutrition_fetch import get_nutrition_with_fallback
from agent_analyzer import analyze_menu_with_preferences
from config import DEBUG_MODE

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Menu Nutrition Analyzer",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'dishes' not in st.session_state:
    st.session_state.dishes = None
if 'dishes_with_nutrition' not in st.session_state:
    st.session_state.dishes_with_nutrition = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header"> AI Menu Nutrition Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Make healthier dining choices with AI-powered nutrition analysis</div>',
            unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - USER PREFERENCES
# ============================================================================

with st.sidebar:
    st.header("👤 Your Dietary Profile")

    goal = st.selectbox(
        "🎯 Health Goal",
        ["Weight Loss", "Muscle Gain", "Maintain Health", "General Wellness"],
        help="Select your primary health objective"
    )

    diet_type = st.selectbox(
        "🥗 Dietary Preference",
        ["None", "Vegan", "Vegetarian", "Keto", "Paleo", "Low-Carb", "Mediterranean"],
        help="Choose your dietary restrictions or preferences"
    )

    calorie_target = st.slider(
        "🔥 Target Calories per Meal",
        min_value=300,
        max_value=1200,
        value=600,
        step=50,
        help="Your ideal calorie intake for this meal"
    )

    allergies = st.multiselect(
        "⚠️ Allergies & Restrictions",
        ["Nuts", "Dairy", "Gluten", "Shellfish", "Eggs", "Soy", "Fish"],
        help="Select any food allergies or intolerances"
    )

    st.divider()

    st.info("💡 **Tip:** Upload a clear photo of the menu for best results")

    # Reset button
    if st.button("🔄 Reset Analysis"):
        st.session_state.dishes = None
        st.session_state.dishes_with_nutrition = None
        st.session_state.analysis = None
        st.rerun()

# ============================================================================
# MAIN CONTENT - UPLOAD & DISPLAY
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Menu Photo")
    uploaded_file = st.file_uploader(
        "Choose a menu image (JPG, PNG)",
        type=['jpg', 'jpeg', 'png'],
        help="Take a clear, well-lit photo of the restaurant menu"
    )

    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Menu", use_column_width=True)

with col2:
    if uploaded_file:
        st.subheader(" Analysis Progress")

        # Analyze button
        if st.button(" Analyze Menu", type="primary", use_container_width=True):

            # ================================================================
            # STEP 1: EXTRACT DISHES FROM IMAGE
            # ================================================================
            with st.status(" Extracting dishes from menu...", expanded=True) as status:
                st.write(" Using GPT-4 Vision to read menu...")

                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    dishes = extract_menu_from_image(uploaded_file)
                    dishes = validate_extracted_dishes(dishes)

                    if dishes:
                        st.session_state.dishes = dishes
                        st.write(f"✅ Found **{len(dishes)}** dishes!")
                        status.update(label="✅ Extraction complete!", state="complete")
                    else:
                        st.error("❌ Could not extract dishes. Try a clearer photo.")
                        status.update(label="❌ Extraction failed", state="error")
                        st.stop()

                except Exception as e:
                    st.error(f"❌ Error during extraction: {str(e)}")
                    status.update(label="❌ Extraction failed", state="error")
                    st.stop()

            # ================================================================
            # STEP 2: FETCH NUTRITION DATA
            # ================================================================
            if st.session_state.dishes:
                with st.status(" Fetching nutrition data...", expanded=True) as status:
                    st.write(" Querying nutrition databases...")

                    try:
                        progress_bar = st.progress(0)
                        dishes_with_nutrition = []

                        for i, dish in enumerate(st.session_state.dishes):
                            nutrition = get_nutrition_with_fallback(
                                dish['name'],
                                dish.get('description', '')
                            )

                            if nutrition:
                                dishes_with_nutrition.append(nutrition)

                            # Update progress
                            progress_bar.progress((i + 1) / len(st.session_state.dishes))

                        st.session_state.dishes_with_nutrition = dishes_with_nutrition

                        if dishes_with_nutrition:
                            st.write(f"✅ Retrieved nutrition for **{len(dishes_with_nutrition)}** dishes!")
                            status.update(label="✅ Nutrition data fetched!", state="complete")
                        else:
                            st.warning("⚠️ Could not find nutrition data for any dishes.")
                            status.update(label="⚠️ No nutrition data found", state="error")
                            st.stop()

                    except Exception as e:
                        st.error(f"❌ Error fetching nutrition: {str(e)}")
                        status.update(label="❌ Nutrition fetch failed", state="error")
                        st.stop()

            # ================================================================
            # STEP 3: AI AGENT ANALYSIS
            # ================================================================
            if st.session_state.get('dishes_with_nutrition'):
                with st.status("🧠 Generating personalized recommendations...", expanded=True) as status:
                    st.write(" AI agent analyzing menu for your profile...")

                    try:
                        user_prefs = {
                            "goal": goal.lower().replace(" ", "_"),
                            "diet_type": diet_type.lower(),
                            "allergies": [a.lower() for a in allergies],
                            "calorie_target": calorie_target
                        }

                        analysis = analyze_menu_with_preferences(
                            st.session_state.dishes_with_nutrition,
                            user_prefs
                        )

                        st.session_state.analysis = analysis
                        st.write("✅ Analysis complete!")
                        status.update(label="✅ Recommendations ready!", state="complete")

                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        status.update(label="❌ Analysis failed", state="error")
                        st.stop()

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.get('analysis'):
    analysis = st.session_state.analysis

    st.divider()
    st.header(" Your Personalized Analysis")

    # ========================================================================
    # TOP METRICS
    # ========================================================================
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Dishes Analyzed", len(st.session_state.dishes_with_nutrition))
    with metric_cols[1]:
        st.metric("Top Recommendations", len(analysis.get('top_picks', [])))
    with metric_cols[2]:
        st.metric("Dishes to Avoid", len(analysis.get('avoid', [])))
    with metric_cols[3]:
        st.metric("Meal Combos", len(analysis.get('meal_combos', [])))

    st.divider()

    # ========================================================================
    # TOP PICKS
    # ========================================================================
    st.subheader("⭐ Best Choices for You")

    if analysis.get('top_picks'):
        for i, pick in enumerate(analysis['top_picks'][:3], 1):
            with st.expander(f"#{i} {pick['name']}", expanded=(i == 1)):
                st.markdown(f"**Why it's great:** {pick['why_good']}")
                st.info(f" {pick['nutrition_highlights']}")
                if pick.get('eating_tips'):
                    st.success(f"💡 Pro tip: {pick['eating_tips']}")
    else:
        st.info("No top picks available")

    # ========================================================================
    # MEAL COMBINATIONS
    # ========================================================================
    if analysis.get('meal_combos'):
        st.divider()
        st.subheader(" Recommended Meal Combinations")

        for combo in analysis['meal_combos']:
            with st.container():
                st.markdown(f"### {' + '.join(combo['items'])}")

                combo_cols = st.columns(4)
                combo_cols[0].metric("Calories", f"{combo['total_calories']}")
                combo_cols[1].metric("Protein", f"{combo['total_protein']}g")
                combo_cols[2].metric("Carbs", f"{combo['total_carbs']}g")
                combo_cols[3].metric("Fat", f"{combo['total_fat']}g")

                st.success(f" {combo['why_good']}")
                if combo.get('cost_estimate'):
                    st.caption(f" Estimated cost: {combo['cost_estimate']}")

                st.divider()

    # ========================================================================
    # DISHES TO AVOID
    # ========================================================================
    if analysis.get('avoid'):
        st.divider()
        st.subheader("⚠️ Dishes to Avoid")
        for avoid in analysis['avoid']:
            st.warning(f"**{avoid['name']}**: {avoid['reason']}")

    # ========================================================================
    # ALLERGEN WARNINGS
    # ========================================================================
    if analysis.get('allergen_warnings'):
        st.divider()
        st.subheader("🚨 Allergen Alerts")
        for warning in analysis['allergen_warnings']:
            st.error(warning)

    # ========================================================================
    # GENERAL ADVICE
    # ========================================================================
    if analysis.get('general_advice'):
        st.divider()
        st.info(f"💡 **General Advice:** {analysis['general_advice']}")

    # ========================================================================
    # FULL RANKINGS (COLLAPSIBLE)
    # ========================================================================
    with st.expander(" See All Dishes Ranked"):
        if analysis.get('ranked_dishes'):
            for dish in analysis['ranked_dishes']:
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.markdown(f"**#{dish['rank']}**")
                with col2:
                    st.markdown(f"**{dish['name']}**")
                    st.caption(dish['reason'])
                with col3:
                    st.markdown(f"Score: {dish['score']}/100")
        else:
            st.info("No ranking data available")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p> This app shows only Demo | Powered by GPT-4 Vision & Nutrition APIs</p>
        <p> Remember: This tool provides suggestions. Always consult healthcare professionals for medical advice.</p>
    </div>
""", unsafe_allow_html=True)