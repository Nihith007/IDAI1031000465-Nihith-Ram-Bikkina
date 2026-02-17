"""
CoachBot AI - Smart Fitness Assistance Web Application
Powered by Google Gemini 2.5 Flash
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoachBot AI - Your Personal Fitness Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS (identical to previous app) ─────────────────────────────────────────
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1E88E5;
    }
    .output-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1E88E5;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ────────────────────────────────────────────────────────────────────────────
# TABULAR FUNCTIONS  (identical to previous app)
# ────────────────────────────────────────────────────────────────────────────

def create_weekly_training_table(training_days=None):
    if training_days is None:
        training_days = {
            'Monday':    {'Intensity': 8, 'Focus': 'Strength Training',        'Duration': '60 min'},
            'Tuesday':   {'Intensity': 6, 'Focus': 'Cardio/Endurance',         'Duration': '45 min'},
            'Wednesday': {'Intensity': 9, 'Focus': 'Sport-Specific Skills',    'Duration': '75 min'},
            'Thursday':  {'Intensity': 5, 'Focus': 'Recovery/Mobility',        'Duration': '30 min'},
            'Friday':    {'Intensity': 7, 'Focus': 'Strength + Conditioning',  'Duration': '60 min'},
            'Saturday':  {'Intensity': 4, 'Focus': 'Light Cardio',             'Duration': '30 min'},
            'Sunday':    {'Intensity': 2, 'Focus': 'Rest/Active Recovery',     'Duration': '20 min'},
        }
    df = pd.DataFrame.from_dict(training_days, orient='index')
    df.index.name = 'Day'
    df.reset_index(inplace=True)
    return df

def create_training_distribution_table(training_types=None):
    if training_types is None:
        training_types = {
            'Strength Training':    30,
            'Cardio/Endurance':     25,
            'Skill Work':           25,
            'Flexibility/Mobility': 10,
            'Rest/Recovery':        10,
        }
    df = pd.DataFrame(list(training_types.items()), columns=['Training Type', 'Percentage (%)'])
    df['Hours per Week'] = (df['Percentage (%)'] / 100 * 10).round(1)
    return df

def create_nutrition_table(calorie_goal='Maintenance'):
    data = {
        'Nutrient':       ['Protein', 'Carbohydrates', 'Fats', 'Total Calories'],
        'Percentage':     ['30%', '45%', '25%', '100%'],
        'Grams per Day':  ['150g', '280g', '70g', '-'],
        'Calories':       ['600 kcal', '1120 kcal', '630 kcal', '2350 kcal'],
    }
    return pd.DataFrame(data)

def create_weekly_meal_plan_table():
    meals = {
        'Day':       ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
        'Breakfast': ['Oatmeal + Eggs','Greek Yogurt + Fruits','Whole Grain Toast + Avocado',
                      'Protein Smoothie','Scrambled Eggs + Veggies','Pancakes + Berries','Omelet + Toast'],
        'Lunch':     ['Chicken + Rice + Veggies','Fish + Quinoa Salad','Turkey Wrap + Soup',
                      'Pasta + Lean Meat','Grilled Chicken Salad','Rice Bowl + Protein','Sandwich + Fruit'],
        'Dinner':    ['Salmon + Sweet Potato','Lean Beef + Brown Rice','Chicken Stir-fry',
                      'Fish + Vegetables','Turkey + Quinoa','Grilled Chicken + Pasta','Lean Meat + Rice'],
        'Snacks':    ['Protein Bar + Nuts','Fruit + Cheese','Hummus + Veggies',
                      'Greek Yogurt','Trail Mix','Protein Shake','Fruit + Nut Butter'],
    }
    return pd.DataFrame(meals)

def create_exercise_table(exercises=None):
    if exercises is None:
        exercises = {
            'Exercise':   ['Squats','Bench Press','Deadlifts','Pull-ups','Shoulder Press',
                           'Lunges','Rows','Core Work'],
            'Sets':       [4, 4, 3, 3, 3, 3, 4, 3],
            'Reps':       ['8-10','8-10','6-8','8-12','10-12','10 each leg','10-12','15-20'],
            'Rest (sec)': [90, 90, 120, 90, 60, 60, 75, 45],
            'Notes':      ['Focus on form','Control the weight','Keep back straight',
                           'Use assistance if needed','Full range of motion','Maintain balance',
                           'Squeeze at top','Engage core throughout'],
        }
    return pd.DataFrame(exercises)

def create_progress_tracking_table(weeks=8):
    data = {
        'Week':             list(range(1, weeks + 1)),
        'Strength (%)':     [20,30,42,55,65,75,82,90,92,94,95,96][:weeks],
        'Endurance (%)':    [25,35,45,58,68,76,84,92,93,94,95,96][:weeks],
        'Skill Level (%)':  [30,38,48,58,68,76,83,89,90,91,92,93][:weeks],
        'Body Weight (kg)': [70,70.5,71,71.2,71.5,71.8,72,72.2,72.3,72.4,72.5,72.6][:weeks],
        'Notes':            ['Baseline','Good progress','Increasing intensity','Maintaining form',
                             'Peak week','Recovery focus','Final push','Assessment week',
                             'Consolidation','Advanced','Elite','Peak'][:weeks],
    }
    return pd.DataFrame(data)

def create_injury_recovery_table():
    data = {
        'Phase':      ['Week 1-2','Week 3-4','Week 5-6','Week 7-8','Week 9+'],
        'Focus':      ['Pain Management','Gentle Movement','Strength Building',
                       'Sport-Specific Work','Full Training'],
        'Intensity':  ['Very Low (2-3/10)','Low (3-4/10)','Moderate (5-6/10)',
                       'High (7-8/10)','Full (9-10/10)'],
        'Activities': ['Ice, Rest, Gentle Stretching','Pool Work, Light Mobility',
                       'Resistance Bands, Bodyweight','Light Sport Drills','Full Practice'],
        'Red Flags':  ['Sharp pain, Swelling','Persistent pain','Limited ROM',
                       'Pain during sport moves','Recurring issues'],
    }
    return pd.DataFrame(data)

def display_tabular_dashboard(feature_type, training_frequency, training_duration):
    st.markdown("---")
    st.markdown("## 📊 Training Schedule & Breakdown (Tables)")
    st.markdown("*Organized data for easy tracking and reference*")

    st.markdown("### 📅 Weekly Training Schedule")
    st.dataframe(create_weekly_training_table(), use_container_width=True, hide_index=True)

    if any(k in feature_type for k in ["Workout", "Training", "Strength"]):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Exercise Routine")
            st.dataframe(create_exercise_table(), use_container_width=True, hide_index=True)
        with col2:
            st.markdown("### 📈 Training Distribution")
            st.dataframe(create_training_distribution_table(), use_container_width=True, hide_index=True)
        st.markdown("### 📊 8-Week Progress Tracking")
        st.dataframe(create_progress_tracking_table(8), use_container_width=True, hide_index=True)

    elif "Nutrition" in feature_type:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🍽️ Macro Breakdown")
            st.dataframe(create_nutrition_table(), use_container_width=True, hide_index=True)
        with col2:
            st.markdown("### 📋 Meal Calorie Distribution")
            meal_dist = pd.DataFrame(
                [('Breakfast',25),('Lunch',30),('Dinner',30),('Snacks',15)],
                columns=['Meal','Calorie %']
            )
            st.dataframe(meal_dist, use_container_width=True, hide_index=True)
        st.markdown("### 🗓️ Weekly Meal Plan")
        st.dataframe(create_weekly_meal_plan_table(), use_container_width=True, hide_index=True)

    elif any(k in feature_type for k in ["Recovery", "Mobility"]):
        st.markdown("### 🏥 Recovery Timeline")
        st.dataframe(create_injury_recovery_table(), use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧘 Recovery Activities")
            recovery_dist = pd.DataFrame(
                [('Stretching',30),('Foam Rolling',20),('Low Impact Cardio',25),('Rest',25)],
                columns=['Activity','Time %']
            )
            st.dataframe(recovery_dist, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("### 📊 Progress Tracking")
            pt = create_progress_tracking_table(8)
            st.dataframe(pt[['Week','Strength (%)','Endurance (%)']], use_container_width=True, hide_index=True)

    elif any(k in feature_type for k in ["Endurance", "Speed"]):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🏃 Training Types")
            training_dist = pd.DataFrame(
                [('Interval Training',35),('Long Distance',30),('Speed Work',20),('Recovery Runs',15)],
                columns=['Type','Percentage %']
            )
            st.dataframe(training_dist, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("### 📈 Training Distribution")
            st.dataframe(create_training_distribution_table(), use_container_width=True, hide_index=True)
        st.markdown("### 📊 12-Week Progress Plan")
        st.dataframe(create_progress_tracking_table(12), use_container_width=True, hide_index=True)

    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📋 Training Distribution")
            default_dist = pd.DataFrame(
                [('Physical Training',40),('Skill Development',30),('Mental Training',15),('Recovery',15)],
                columns=['Category','Percentage %']
            )
            st.dataframe(default_dist, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("### 📊 Progress Tracking")
            pt = create_progress_tracking_table(8)
            st.dataframe(pt[['Week','Strength (%)','Skill Level (%)']], use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────────────────────
# AI HELPER
# ────────────────────────────────────────────────────────────────────────────
def get_ai_response(target_model, prompt):
    try:
        response = target_model.generate_content(prompt)
        if response.candidates and response.candidates[0].content.parts:
            raw = response.candidates[0].content.parts[0].text
            return (raw.replace("<br>", " ").replace("</br>", " ")
                       .replace("<div>", "").replace("</div>", ""))
        return "The AI Coach is currently unavailable. Please check your connection."
    except Exception as e:
        return f"Model Error: {str(e)}"


# ────────────────────────────────────────────────────────────────────────────
# HEADER
# ────────────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🏋️ CoachBot AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Personal AI Fitness & Sports Coach - Powered by Gemini 2.5 Flash</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #1E88E5; font-weight: 500;">✨ Now with Organized Training Tables & Data ✨</p>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR  (identical to previous app)
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = None
    try:
        if 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
            st.success("✅ API Key loaded from secrets!")
            genai.configure(api_key=api_key)
            st.session_state.api_key_configured = True
        else:
            api_key = st.text_input("Enter Gemini API Key", type="password",
                                    help="Get your key from Google AI Studio or add to Streamlit secrets")
            if api_key:
                genai.configure(api_key=api_key)
                st.session_state.api_key_configured = True
                st.success("✅ API Key Configured!")
    except Exception:
        api_key = st.text_input("Enter Gemini API Key", type="password",
                                help="Get your key from Google AI Studio")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                st.session_state.api_key_configured = True
                st.success("✅ API Key Configured!")
            except Exception as e:
                st.error(f"❌ Invalid API Key: {str(e)}")
                st.session_state.api_key_configured = False

    st.markdown("---")
    st.header("👤 Your Profile")
    user_name   = st.text_input("Name", placeholder="John Doe")
    user_age    = st.number_input("Age", min_value=10, max_value=100, value=15)
    user_gender = st.selectbox("Gender", ["Male","Female","Other","Prefer not to say"])

    st.markdown("---")
    st.header("⚽ Sport Details")
    sport = st.selectbox("Select Your Sport", [
        "Football/Soccer","Cricket","Basketball","Athletics/Track & Field",
        "Tennis","Swimming","Volleyball","Badminton","Hockey","Other"
    ])

    position_options = {
        "Football/Soccer":          ["Goalkeeper","Defender","Midfielder","Forward/Striker","Winger"],
        "Cricket":                  ["Batsman","Bowler (Fast)","Bowler (Spin)","All-rounder","Wicket-keeper"],
        "Basketball":               ["Point Guard","Shooting Guard","Small Forward","Power Forward","Center"],
        "Athletics/Track & Field":  ["Sprinter","Middle Distance","Long Distance","Jumper","Thrower"],
        "Tennis":                   ["Singles Player","Doubles Player","Baseline Player","Serve-and-Volley"],
        "Swimming":                 ["Freestyle","Backstroke","Breaststroke","Butterfly","Individual Medley"],
        "Volleyball":               ["Setter","Outside Hitter","Middle Blocker","Libero","Opposite Hitter"],
        "Badminton":                ["Singles Player","Doubles Player","Mixed Doubles"],
        "Hockey":                   ["Forward","Midfielder","Defender","Goalkeeper"],
        "Other":                    ["General Athlete"],
    }
    position = st.selectbox("Player Position", position_options.get(sport, ["General"]))

    st.markdown("---")
    st.header("🎯 Fitness Details")
    fitness_level   = st.select_slider("Current Fitness Level",
                                       options=["Beginner","Intermediate","Advanced","Elite"])
    injury_history  = st.text_area("Injury History/Risk Zones",
                                   placeholder="e.g., Previous ankle sprain, knee sensitivity")

    st.markdown("---")
    st.header("🍽️ Nutrition Preferences")
    diet_type    = st.selectbox("Diet Type", ["Vegetarian","Non-Vegetarian","Vegan","Pescatarian"])
    allergies    = st.text_input("Allergies/Food Restrictions", placeholder="e.g., Nuts, dairy, gluten")
    calorie_goal = st.select_slider("Daily Calorie Goal",
                                    options=["Maintenance","Deficit (Weight Loss)","Surplus (Muscle Gain)"])


# ────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ────────────────────────────────────────────────────────────────────────────
if st.session_state.api_key_configured:

    # ── TWO TABS ──────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📊 Smart Assistant", "🧠 Custom Coach"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1  —  SMART ASSISTANT  (identical to previous app)
    # ══════════════════════════════════════════════════════════════════════
    with tab1:

        st.header("🎯 What would you like CoachBot to help you with?")

        feature = st.selectbox("Select a Feature", [
            "1. Full-Body Workout Plan for [Position] in [Sport]",
            "2. Safe Recovery Training Schedule for Athlete with [Injury]",
            "3. Tactical Coaching Tips to Improve [Skill] in [Sport]",
            "4. Week-Long Nutrition Guide for Young Athlete",
            "5. Personalized Warm-up & Cooldown Routine",
            "6. Mental Focus Routines for Tournaments",
            "7. Hydration & Electrolyte Strategy",
            "8. Pre-Match Visualization Techniques",
            "9. Positional Decision-Making Drills",
            "10. Mobility Workouts for Post-Injury Recovery",
        ])

        col1, col2 = st.columns(2)
        with col1:
            training_intensity = st.select_slider("Training Intensity",
                                                  options=["Low","Moderate","High","Very High"])
            training_duration  = st.selectbox("Training Duration per Session",
                                              ["30 minutes","45 minutes","60 minutes","90 minutes","120 minutes"])
        with col2:
            training_frequency = st.selectbox("Training Frequency",
                                              ["2-3 times/week","4-5 times/week","6 times/week","Daily"])
            specific_goal      = st.text_input("Specific Goal",
                                              placeholder="e.g., Improve stamina, recover from injury, tournament prep")

        with st.expander("🔧 Advanced Settings (Optional)"):
            temperature = st.slider("AI Creativity Level", 0.0, 1.0, 0.5, 0.1,
                                    help="Lower = conservative  |  Higher = creative")
            st.markdown("---")
            st.markdown("**📊 Display Settings**")
            show_charts = st.checkbox("Show Training Tables & Data", value=True,
                                      help="Display organized tables with your plan")

        if st.button("🚀 Generate Personalized Plan", type="primary"):

            user_context = f"""
            User Profile:
            - Name: {user_name if user_name else 'Athlete'}
            - Age: {user_age}
            - Gender: {user_gender}
            - Sport: {sport}
            - Position: {position}
            - Fitness Level: {fitness_level}
            - Injury History: {injury_history if injury_history else 'None'}
            - Diet Type: {diet_type}
            - Allergies: {allergies if allergies else 'None'}
            - Calorie Goal: {calorie_goal}
            - Training Intensity: {training_intensity}
            - Training Duration: {training_duration}
            - Training Frequency: {training_frequency}
            - Specific Goal: {specific_goal if specific_goal else 'General improvement'}
            """

            prompts = {
                "1. Full-Body Workout Plan for [Position] in [Sport]": f"""
                As an experienced sports coach, create a comprehensive full-body workout plan for a {position} in {sport}.
                {user_context}
                Please provide:
                1. Detailed workout routine with exercises, sets, and reps
                2. Sport-specific exercises for their position
                3. Safety considerations based on injury history
                4. Progressive overload strategy
                5. Rest and recovery recommendations
                6. Weekly schedule with training days
                Format the response in a clear, structured manner with tables where appropriate.
                """,

                "2. Safe Recovery Training Schedule for Athlete with [Injury]": f"""
                As a sports physiotherapist and coach, create a safe recovery training schedule for an athlete with: {injury_history if injury_history else 'General recovery needs'}.
                {user_context}
                Focus on:
                1. Low-impact exercises suitable for injury recovery
                2. Gradual progression back to full training (week-by-week plan)
                3. Specific exercises to AVOID based on injury history
                4. Flexibility and mobility work
                5. Timeline for recovery phases (Week 1, 2, 3, 4, etc.)
                6. Warning signs to watch for and when to rest
                7. Return-to-sport criteria
                Prioritize safety and long-term health over quick returns. Provide a structured recovery timeline.
                """,

                "3. Tactical Coaching Tips to Improve [Skill] in [Sport]": f"""
                As a tactical coach specializing in {sport}, provide advanced coaching tips for a {position}.
                {user_context}
                Include:
                1. Position-specific tactical awareness and responsibilities
                2. Game-reading skills to develop
                3. Decision-making scenarios and solutions
                4. Communication strategies with teammates
                5. Common tactical mistakes to avoid in this position
                6. Training drills to improve tactical understanding
                7. Professional examples and best practices
                Use specific examples from {sport} where relevant. Provide actionable tips.
                """,

                "4. Week-Long Nutrition Guide for Young Athlete": f"""
                As a sports nutritionist, create a comprehensive week-long nutrition guide for a {user_age}-year-old athlete.
                {user_context}
                Provide:
                1. Daily meal plans for 7 days (Breakfast, Lunch, Dinner, Snacks)
                2. Pre-training and post-training nutrition strategies
                3. Macro breakdown (Proteins, Carbs, Fats) in a table format
                4. Specific foods to support {sport} performance
                5. Timing of meals around training sessions
                6. Hydration recommendations throughout the day
                7. Age-appropriate supplement suggestions (if any)
                8. Sample grocery list
                Consider dietary restrictions ({diet_type}, allergies: {allergies if allergies else 'none'}) and calorie goals ({calorie_goal}).
                Present meal plans in an organized table format for easy reference.
                """,

                "5. Personalized Warm-up & Cooldown Routine": f"""
                Create a personalized warm-up and cooldown routine specifically for a {position} in {sport}.
                {user_context}
                Include:
                1. Dynamic warm-up routine (10-15 minutes) - list specific exercises
                2. Sport-specific activation drills for {sport}
                3. Position-specific movement preparation for {position}
                4. Modifications based on injury history: {injury_history if injury_history else 'none'}
                5. Cooldown routine with static stretching (10-15 minutes)
                6. Foam rolling sequence and mobility work
                7. Breathing and recovery techniques
                Make it practical and easy to follow. Provide sets and duration for each exercise.
                """,

                "6. Mental Focus Routines for Tournaments": f"""
                As a sports psychologist, create a comprehensive mental preparation program for a {user_age}-year-old {position} preparing for tournaments in {sport}.
                {user_context}
                Cover:
                1. Pre-tournament mental preparation (weeks before)
                2. Week-of-tournament daily routines
                3. Day-before and morning-of mental checklist
                4. Visualization techniques specific to {sport} and {position}
                5. Pressure management and performance anxiety strategies
                6. Focus and concentration drills
                7. Dealing with nervousness and pre-game jitters
                8. Post-performance reflection techniques
                9. Building confidence and positive self-talk
                Make it age-appropriate for a {user_age}-year-old and practical to implement.
                """,

                "7. Hydration & Electrolyte Strategy": f"""
                Design a comprehensive hydration and electrolyte strategy for a young {sport} athlete.
                {user_context}
                Provide:
                1. Daily water intake recommendations (in liters/ml)
                2. Pre-training hydration protocol (timing and amounts)
                3. During-training hydration strategy
                4. Post-training rehydration plan
                5. Electrolyte balance strategies and when to use sports drinks
                6. Signs of dehydration to watch for
                7. Sport-specific hydration needs for {sport}
                8. Hydration strategies for different weather conditions
                9. Recommended drinks and timing throughout the day
                10. Weekly hydration schedule table
                Consider their age ({user_age}) and training intensity ({training_intensity}).
                Present in an organized format with clear guidelines.
                """,

                "8. Pre-Match Visualization Techniques": f"""
                Teach effective pre-match visualization techniques for a {position} in {sport}.
                {user_context}
                Include:
                1. Step-by-step visualization process (how to do it)
                2. What specifically to visualize as a {position} in {sport}
                3. Successful plays and scenarios to imagine
                4. Positioning and movement patterns to rehearse mentally
                5. When to practice visualization (timeline before match)
                6. Combining visualization with breathing techniques
                7. Confidence-building mental imagery
                8. Dealing with negative thoughts and doubts
                9. Creating a consistent pre-match mental routine
                10. Sample visualization script for {sport}
                Make it practical for a {user_age}-year-old athlete to implement independently.
                """,

                "9. Positional Decision-Making Drills": f"""
                Create position-specific decision-making drills for a {position} in {sport}.
                {user_context}
                Provide:
                1. Situational awareness drills specific to {position}
                2. Quick decision-making exercises under pressure
                3. Game-like scenarios to practice (at least 5 scenarios)
                4. Reading the game/opposition drills
                5. Positioning and movement decision drills
                6. Progressive difficulty levels (beginner to advanced)
                7. Solo practice drills (can do alone)
                8. Partner/team drills (with teammates)
                9. Video analysis recommendations
                10. Performance metrics to track improvement
                Focus on improving game intelligence and decision-making speed for {position}.
                Provide clear instructions for each drill.
                """,

                "10. Mobility Workouts for Post-Injury Recovery": f"""
                Create a comprehensive mobility and flexibility program for post-injury recovery.
                {user_context}
                Include:
                1. Gentle mobility exercises for affected areas: {injury_history if injury_history else 'general recovery'}
                2. Full-body mobility routine (not just injured area)
                3. Dynamic stretching sequences
                4. Yoga-inspired movements for athletes
                5. Frequency recommendations (daily schedule)
                6. Duration for each session
                7. Progression markers (when to advance)
                8. Exercises to avoid during recovery
                9. Pain management and when to stop
                10. Timeline: Week 1-2, Week 3-4, Week 5-6, etc.
                11. Return-to-sport mobility standards
                Emphasize safety and gradual progression. Provide detailed instructions with sets/reps/duration.
                Make it specific to {sport} demands.
                """,
            }

            selected_prompt = prompts.get(feature, prompts["1. Full-Body Workout Plan for [Position] in [Sport]"])

            try:
                with st.spinner("🤖 CoachBot is creating your personalized plan..."):
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        generation_config={
                            "temperature": temperature,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_output_tokens": 8192,
                        }
                    )
                    response = model.generate_content(selected_prompt)

                    if not response.text:
                        st.error("⚠️ Response was blocked or incomplete. Please try again.")
                        st.stop()

                    st.markdown("---")
                    st.markdown("## 📋 Your Personalized Plan")
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)

                    if show_charts:
                        display_tabular_dashboard(feature, training_frequency, training_duration)

                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "feature":   feature,
                        "response":  response.text,
                    })

                    st.download_button(
                        label="📥 Download Plan as Text File",
                        data=response.text,
                        file_name=f"coachbot_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                    )
                    st.success("✅ Plan generated successfully! Review it carefully and consult with a coach if needed.")

            except Exception as e:
                st.error(f"❌ Error generating plan: {str(e)}")
                if "quota" in str(e).lower():
                    st.warning("⚠️ API quota exceeded. Please wait a moment and try again.")
                elif "api key" in str(e).lower():
                    st.warning("⚠️ API key issue. Please verify your API key is correct and active.")
                elif "blocked" in str(e).lower():
                    st.warning("⚠️ Content blocked by safety filters. Try rephrasing your request.")
                else:
                    st.info("💡 Try: checking your API key · simplifying your request · waiting a moment · checking your internet connection")

        # Chat history
        if st.session_state.chat_history:
            st.markdown("---")
            with st.expander("📜 View Previous Plans"):
                for entry in reversed(st.session_state.chat_history[-5:]):
                    st.markdown(f"**{entry['timestamp']}** - {entry['feature']}")
                    st.text(entry['response'][:200] + "...")
                    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2  —  CUSTOM COACH  (from the pasted code)
    # ══════════════════════════════════════════════════════════════════════
    with tab2:

        st.subheader("🧠 Custom Coach Consultation")
        user_query = st.text_area(
            "Ask a specific coaching question:",
            placeholder="e.g., Suggest 3 drills for explosive speed.",
            height=130,
        )

        col_a, col_b = st.columns([1, 2])
        with col_a:
            intensity_val = st.slider("Advice Intensity", 1, 100, 40)
            ai_temp       = intensity_val / 100.0
            st.caption(f"Temperature: **{ai_temp:.2f}**")

        if st.button("Ask AI Coach", type="primary"):
            if not user_query.strip():
                st.warning("Please type a question before submitting.")
            else:
                custom_prompt = (
                    f"User Question: {user_query}. Advice Intensity: {intensity_val}/100. "
                    "STRICT RULES: Output ONLY a short, technical Markdown table. NO HTML tags like <br>. "
                    "Keep descriptions extremely concise."
                )
                with st.spinner("Consulting AI Coach..."):
                    custom_model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        generation_config={"temperature": ai_temp, "max_output_tokens": 8192}
                    )
                    answer = get_ai_response(custom_model, custom_prompt)

                st.markdown("---")
                st.info("📋 Quick Coaching Chart:")
                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown('</div>', unsafe_allow_html=True)

                # Reference tables beneath the answer
                st.markdown("### 📊 Reference Training Tables")
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown("**📅 Weekly Schedule**")
                    st.dataframe(create_weekly_training_table(), use_container_width=True, hide_index=True)
                with r2:
                    st.markdown("**📈 Training Distribution**")
                    st.dataframe(create_training_distribution_table(), use_container_width=True, hide_index=True)


# ── Landing page when no API key ──────────────────────────────────────────
else:
    st.info("👈 Please enter your Gemini API Key in the sidebar to get started.")

    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Get your API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free Gemini API key
    2. **Enter the API Key**: Paste it in the sidebar
    3. **Fill your profile**: Complete your sport and fitness details
    4. **Choose a feature**: Select what you want help with
    5. **Generate your plan**: Click the button and get personalized coaching!
    """)

    st.markdown("### ✨ Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🏋️ Training Plans**
        - Full-body workouts
        - Recovery schedules
        - Strength programs
        - Speed & agility training
        """)
    with col2:
        st.markdown("""
        **🎯 Tactical Coaching**
        - Position-specific tips
        - Decision-making drills
        - Match preparation
        - Mental focus techniques
        """)
    with col3:
        st.markdown("""
        **🍽️ Nutrition & Recovery**
        - Weekly meal plans
        - Hydration strategies
        - Post-injury mobility
        - Tournament prep
        """)

    st.info("📊 **NEW**: Every plan includes organized training tables and schedules automatically!")


# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>CoachBot AI</strong> - Empowering Young Athletes with AI-Powered Coaching</p>
    <p style='font-size: 0.9rem;'>⚠️ Disclaimer: This AI provides general guidance. Always consult with qualified coaches,
    trainers, and medical professionals before starting any new training program.</p>
</div>
""", unsafe_allow_html=True)
