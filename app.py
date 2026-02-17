"""
CoachBot AI - Smart Fitness Assistance Web Application
Powered by Google Gemini 2.5 Flash
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    API_READY = True
except Exception:
    API_READY = False

def get_ai_response(target_model, prompt):
    """Safely call the model and strip stray HTML tags."""
    try:
        response = target_model.generate_content(prompt)
        if response.candidates and response.candidates[0].content.parts:
            raw = response.candidates[0].content.parts[0].text
            clean = (raw
                     .replace("<br>", " ").replace("</br>", " ")
                     .replace("<div>", "").replace("</div>", ""))
            return clean
        return "The AI Coach is currently unavailable. Please check your connection."
    except Exception as e:
        return f"Model Error: {str(e)}"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CoachBot AI - Your Personal Fitness Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS  — same blue theme as previous app
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
.stApp { background-color: #f0f4f8; }

/* Header */
.main-header {
    font-size: 2.6rem;
    color: #1E88E5;
    text-align: center;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.sub-header {
    font-size: 1.05rem;
    color: #555;
    text-align: center;
    margin-bottom: 1.6rem;
}

/* Tabs */
.stTabs [role="tablist"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}
.stTabs [role="tab"] {
    color: #555;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 22px;
}
.stTabs [aria-selected="true"] {
    background: #1E88E5 !important;
    color: #ffffff !important;
}

/* Section sub-headers */
h2, h3 { color: #1E88E5 !important; }

/* Output card */
.output-box {
    background: #ffffff;
    border: 2px solid #1E88E5;
    border-radius: 12px;
    padding: 1.4rem;
    margin-top: 0.8rem;
}

/* Feature highlight box */
.feature-box {
    background: #e8f4fe;
    border-left: 5px solid #1E88E5;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #333;
}

/* Nutrition info banner */
.info-banner {
    background: #fff8e1;
    border-left: 4px solid #FFC107;
    border-radius: 6px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.92rem;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
    color: #ffffff;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    width: 100%;
    transition: opacity 0.2s, transform 0.15s;
}
div.stButton > button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}

/* DataFrames */
.dataframe thead th {
    background-color: #1E88E5 !important;
    color: #ffffff !important;
    font-weight: 700;
    padding: 10px 14px !important;
}
.dataframe tbody td {
    padding: 9px 14px !important;
    border-bottom: 1px solid #e0e8f0;
}
.dataframe tbody tr:nth-child(even) td { background-color: #f0f6ff; }
.dataframe tbody tr:hover td          { background-color: #daeeff; }

/* Footer */
.footer-text {
    text-align: center;
    color: #888;
    font-size: 0.82rem;
    padding: 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
positions_map = {
    "Football":   ["Striker", "Midfielder", "Defender", "Goalkeeper", "Winger"],
    "Cricket":    ["Batsman", "Fast Bowler", "Spin Bowler", "Wicket Keeper", "All-Rounder"],
    "Basketball": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
    "Athletics":  ["Sprinter", "Long Distance", "Jumper", "Thrower"],
    "Swimming":   ["Freestyle", "Breaststroke", "Butterfly", "Backstroke"],
    "Tennis":     ["Singles", "Doubles Specialist"],
    "Rugby":      ["Forward", "Back"],
    "Volleyball": ["Setter", "Libero", "Attacker", "Blocker"],
    "Badminton":  ["Singles", "Doubles"],
    "Hockey":     ["Forward", "Midfielder", "Defender", "Goalie"],
    "Kabaddi":    ["Raider", "Defender", "All-Rounder"],
}

FEATURES = [
    "1. Full-Body Workout Plan",
    "2. Safe Recovery Training Schedule",
    "3. Tactical Coaching Tips",
    "4. Week-Long Nutrition Guide",
    "5. Warm-up & Cooldown Routine",
    "6. Mental Focus & Tournament Prep",
    "7. Hydration & Electrolyte Strategy",
    "8. Pre-Match Visualization Techniques",
    "9. Positional Decision-Making Drills",
    "10. Mobility Workouts (Post-Injury)",
]

# ─────────────────────────────────────────────
# TABLE BUILDERS
# ─────────────────────────────────────────────
def weekly_schedule_table(intensity):
    scores = {"Low": [4,3,5,2,4,3,1],
              "Moderate": [6,5,7,3,6,4,2],
              "High": [8,6,9,4,7,5,2]}.get(intensity, [6,5,7,3,6,4,2])
    return pd.DataFrame({
        "Day":              ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "Focus":            ["Strength","Cardio / Endurance","Sport-Specific Skills",
                             "Recovery / Mobility","Strength + Conditioning","Light Cardio","Rest"],
        "Duration":         ["60 min","45 min","75 min","30 min","60 min","30 min","Active Rest"],
        "Intensity (1–10)": scores,
    })

def split_table(feature):
    if "Nutrition" in feature or "Hydration" in feature:
        return pd.DataFrame({
            "Nutrient":    ["Protein","Carbohydrates","Fats"],
            "Share":       ["30 %","45 %","25 %"],
            "Grams/Day":   ["150 g","280 g","70 g"],
            "Calories":    ["600 kcal","1 120 kcal","630 kcal"],
        })
    elif "Recovery" in feature or "Mobility" in feature:
        return pd.DataFrame({
            "Phase":   ["Week 1–2","Week 3–4","Week 5–6","Week 7–8"],
            "Focus":   ["Pain management","Gentle movement","Strength rebuild","Sport-specific"],
            "Load":    ["Very low","Low","Moderate","High"],
            "Avoid":   ["All impact","Jumping/cutting","Lateral sprints","Full contact"],
        })
    elif "Hydration" in feature:
        return pd.DataFrame({
            "Period":         ["Before Training","During (per 15 min)","After Training","Rest of Day"],
            "Amount":         ["400–600 ml","150–200 ml","600–800 ml","1.5–2 litres"],
            "Drink Type":     ["Water","Electrolyte mix","Recovery drink","Water + fruit"],
        })
    else:
        return pd.DataFrame({
            "Training Type":      ["Strength","Cardio / Endurance","Skill Work",
                                   "Flexibility / Mobility","Rest / Recovery"],
            "Weekly Share":       ["30 %","25 %","25 %","10 %","10 %"],
            "Est. Hours / Week":  ["3.0 h","2.5 h","2.5 h","1.0 h","1.0 h"],
        })

def exercise_table(feature, sport, position):
    if any(k in feature for k in ["Workout","Strength","Conditioning"]):
        return pd.DataFrame({
            "Exercise":    ["Squats","Lunges","Push-ups","Bent Rows","Shoulder Press","Plank","Core Circuit"],
            "Sets":        [4, 3, 3, 4, 3, 3, 2],
            "Reps":        ["8–10","10/leg","12–15","10–12","10–12","45 s","15–20"],
            "Rest (s)":    [90, 60, 60, 75, 60, 45, 45],
            "Sport Note":  [f"{sport} specific","Balance & knee","Upper push","Upper pull",
                            "Shoulder stability","Core","Full circuit"],
        })
    elif any(k in feature for k in ["Warm","Cooldown"]):
        return pd.DataFrame({
            "Phase":      ["Dynamic Warm-up","Activation","Sport Drills","Cool-down","Static Stretch"],
            "Duration":   ["10 min","8 min","10 min","8 min","10 min"],
            "Exercises":  ["Jog + arm circles","Glutes & hip flexors","Position-specific",
                           "Walk + diaphragm breathing","Hold 30 s each"],
            "Intensity":  ["Low","Low–Med","Med","Very low","—"],
        })
    elif any(k in feature for k in ["Drill","Tactical","Decision"]):
        return pd.DataFrame({
            "Drill":      ["Positioning Grid","Rondo Passing","1v1 Duel","Transition Sprint","Set Piece"],
            "Duration":   ["12 min","10 min","8 min","10 min","10 min"],
            "Players":    ["Team","4 + 1","2","4","Team"],
            "KPI":        ["Zone coverage","Touch count","Win rate","Sprint time","Conversion %"],
            "Position":   [position] * 5,
        })
    elif any(k in feature for k in ["Nutrition","Hydration"]):
        return pd.DataFrame({
            "Meal":       ["Breakfast","Pre-Training","Lunch","Post-Training","Dinner","Evening Snack"],
            "Timing":     ["7:00 AM","9:30 AM","12:30 PM","3:30 PM","7:00 PM","9:00 PM"],
            "Focus":      ["Energy load","Quick fuel","Balanced","Muscle repair","Satiety","Light"],
            "Key Macro":  ["Carbs","Carbs + sugar","Protein + carbs","Protein","Protein + fats","Protein"],
        })
    else:
        return pd.DataFrame({
            "Activity":   ["Foam Rolling","Dynamic Stretch","Yoga Flow","Balance Drills","Breathing"],
            "Duration":   ["10 min","10 min","15 min","10 min","5 min"],
            "Target Area":["Full body","Hip flexors & hamstrings","Full body mobility",
                           "Ankle & knee","Diaphragm / nervous system"],
            "Frequency":  ["Daily","Daily","3× / week","Daily","Daily"],
        })

def progress_table(days):
    weeks = max(1, days // 7)
    s = [min(90, 20 + int(70 / weeks) * i) for i in range(1, weeks + 1)]
    e = [min(92, 25 + int(67 / weeks) * i) for i in range(1, weeks + 1)]
    k = [min(89, 30 + int(59 / weeks) * i) for i in range(1, weeks + 1)]
    notes = (["Build"] * (weeks // 2) + ["Peak"] * (weeks - weeks // 2))[:weeks]
    return pd.DataFrame({
        "Week": list(range(1, weeks + 1)),
        "Strength (%)": s,
        "Endurance (%)": e,
        "Skill (%)": k,
        "Phase": notes,
    })

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">🏋️ CoachBot AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Professional-grade coaching & fitness assistant for young athletes &nbsp;|&nbsp; '
    'Powered by <strong>Gemini 2.5 Flash</strong></p>',
    unsafe_allow_html=True,
)
if not API_READY:
    st.warning("⚠️ API key not found. Add `GOOGLE_API_KEY` to your Streamlit secrets to enable AI responses.")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Smart Assistant", "🧠 Custom Coach"])

# ══════════════════════════════════════════════
# TAB 1  —  SMART ASSISTANT
# ══════════════════════════════════════════════
with tab1:

    # ── 1. Athlete Profile ───────────────────
    st.subheader("1. Athlete Profile")
    c1, c2, c3, c4 = st.columns(4)
    with c1: sport    = st.selectbox("Sport",           list(positions_map.keys()))
    with c2: position = st.selectbox("Position",        positions_map[sport])
    with c3: age      = st.number_input("Age",          10, 50, 18)
    with c4: injury   = st.text_input("Injury History", "None")

    # ── 2. Training Details ──────────────────
    st.subheader("2. Training Details")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        feature = st.selectbox("Coaching Focus", FEATURES)
    with g2:
        goal = st.selectbox("Goal", ["Stamina","Strength","Speed","Recovery","Skill Improvement"])
    with g3:
        intensity_level = st.select_slider("Intensity Level", options=["Low","Moderate","High"])
    with g4:
        days = st.number_input("Duration (Days)", 1, 30, 7)

    # ── Nutrition extras ─────────────────────
    allergy, pref = "None", "N/A"
    if any(k in feature for k in ["Nutrition", "Hydration"]):
        st.markdown(
            '<div class="info-banner">🍎 <strong>Nutrition details required for this feature</strong></div>',
            unsafe_allow_html=True,
        )
        f1, f2 = st.columns(2)
        with f1: pref    = st.selectbox("Meal Preference", ["Non-Veg","Vegetarian","Vegan"])
        with f2: allergy = st.text_input("Food Allergies", "None", key="allergy_t1")

    # ── Advanced settings ─────────────────────
    with st.expander("🔧 Advanced Settings (Optional)"):
        temperature = st.slider("AI Creativity Level", 0.0, 1.0, 0.5, 0.1,
                                help="Lower = consistent/safe  |  Higher = creative")
        show_tables = st.checkbox("Show Training Reference Tables", value=True)

    # ── Generate button ──────────────────────
    if st.button("🚀 Generate Plan", type="primary"):

        prompt = (
            f"Act as a professional sports coach for a {age}-year-old {sport} {position}. "
            f"Goal: {goal}. Intensity: {intensity_level}. Duration: {days} days. "
            f"Injury history: {injury}. Diet: {pref}. Allergies: {allergy}. "
            f"Task: Provide a detailed plan for '{feature}'. "
            "STRICT RULES: Output ONLY a clean Markdown table with relevant columns. "
            "NO HTML tags. Be technically accurate for this athlete's sport and position. "
            "If injury history is not 'None', add a ⚠️ Safety Note row at the end of the table."
        )

        with st.spinner("⏳ AI Coach calculating your personalised plan..."):
            if API_READY:
                model = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    generation_config={"temperature": temperature, "max_output_tokens": 8192},
                )
                result = get_ai_response(model, prompt)
            else:
                result = "*(AI response unavailable — GOOGLE_API_KEY not set in Streamlit secrets)*"

            st.session_state.history.append({
                "Time":     datetime.now().strftime("%H:%M:%S"),
                "Feature":  feature,
                "Sport":    sport,
                "Position": position,
                "Age":      age,
            })

        # ── Output + pie chart ────────────────
        st.markdown("---")
        st.markdown("## 📋 Your Personalised Plan")

        res_col, vis_col = st.columns([2, 1])

        with res_col:
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(
                f"**Feature:** {feature} &nbsp;|&nbsp; "
                f"**Sport:** {sport} — {position} &nbsp;|&nbsp; **Age:** {age}"
            )
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                "📥 Download Plan",
                data=result,
                file_name=f"coachbot_{feature[:20].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
            )

        with vis_col:
            st.subheader("📊 Session Load Split")
            fig, ax = plt.subplots(figsize=(4, 4))
            fig.patch.set_facecolor("#f0f4f8")
            ax.set_facecolor("#f0f4f8")
            ax.pie(
                [20, 60, 20],
                labels=["Warm-up", "Core Work", "Recovery"],
                autopct="%1.1f%%",
                colors=["#FFD700", "#1E88E5", "#32CD32"],
                textprops={"color": "#333", "fontsize": 11},
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
            )
            st.pyplot(fig)
            plt.close(fig)

        # ── Reference tables ─────────────────
        if show_tables:
            st.markdown("---")
            st.markdown("## 📊 Training Reference Tables")
            st.caption("Structured data to complement your AI-generated plan")

            r1, r2 = st.columns(2)
            with r1:
                st.markdown("### 📅 Weekly Schedule")
                st.dataframe(weekly_schedule_table(intensity_level),
                             use_container_width=True, hide_index=True)
            with r2:
                st.markdown("### 🥧 Training / Nutrition Split")
                st.dataframe(split_table(feature),
                             use_container_width=True, hide_index=True)

            r3, r4 = st.columns(2)
            with r3:
                st.markdown("### 💪 Exercise / Activity Breakdown")
                st.dataframe(exercise_table(feature, sport, position),
                             use_container_width=True, hide_index=True)
            with r4:
                st.markdown("### 📈 Progress Tracker")
                st.dataframe(progress_table(days),
                             use_container_width=True, hide_index=True)

        st.success(
            "✅ Plan generated! Always review with a qualified coach or "
            "medical professional before starting."
        )

# ══════════════════════════════════════════════
# TAB 2  —  CUSTOM COACH
# ══════════════════════════════════════════════
with tab2:

    st.subheader("🧠 Custom Coach Consultation")
    st.markdown(
        '<div class="feature-box">'
        "Ask any specific coaching question and receive a concise, "
        "table-formatted answer from your AI coach."
        "</div>",
        unsafe_allow_html=True,
    )

    user_query = st.text_area(
        "Ask a specific coaching question:",
        placeholder="e.g., Suggest 3 drills for explosive speed for a football striker.",
        height=120,
    )

    col_a, col_b = st.columns([1, 2])
    with col_a:
        intensity_val = st.slider("Advice Intensity", 1, 100, 40)
        ai_temp       = intensity_val / 100.0
        st.caption(f"Temperature: **{ai_temp:.2f}** — higher = more creative answers")
    with col_b:
        st.markdown(
            '<div class="info-banner">'
            "💡 <strong>Tip:</strong> Be specific — include sport, position, and goal "
            "for the most accurate coaching advice."
            "</div>",
            unsafe_allow_html=True,
        )

    if st.button("🎯 Ask AI Coach", type="primary"):
        if not user_query.strip():
            st.warning("Please type a question before submitting.")
        else:
            custom_prompt = (
                f"User question: {user_query}. Advice intensity: {intensity_val}/100. "
                "STRICT RULES: Output ONLY a short, precise Markdown table. "
                "NO HTML tags like <br>. Keep each cell concise (max 10 words). "
                "Use relevant columns that directly answer the question."
            )

            with st.spinner("🤖 Consulting your AI Coach..."):
                if API_READY:
                    custom_model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        generation_config={"temperature": ai_temp, "max_output_tokens": 1024},
                    )
                    answer = get_ai_response(custom_model, custom_prompt)
                else:
                    answer = "*(AI response unavailable — GOOGLE_API_KEY not set in Streamlit secrets)*"

            st.markdown("---")
            st.markdown("### 📋 Quick Coaching Chart")
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown("</div>", unsafe_allow_html=True)

            # companion reference tables
            st.markdown("### 📊 General Reference Tables")
            t1, t2 = st.columns(2)
            with t1:
                st.markdown("**Weekly Intensity Schedule (Moderate)**")
                st.dataframe(weekly_schedule_table("Moderate"),
                             use_container_width=True, hide_index=True)
            with t2:
                st.markdown("**Training Type Distribution**")
                st.dataframe(split_table("General"),
                             use_container_width=True, hide_index=True)

    # ── Session history ───────────────────────
    if st.session_state.history:
        st.markdown("---")
        with st.expander("📜 Plans Generated This Session"):
            st.dataframe(
                pd.DataFrame(st.session_state.history),
                use_container_width=True,
                hide_index=True,
            )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p class="footer-text">'
    "🏋️ <strong>CoachBot AI</strong> — Empowering young athletes with AI-powered coaching<br>"
    "⚠️ <em>Disclaimer: This AI provides general guidance only. Always consult a qualified "
    "coach, trainer, or medical professional before beginning any new training programme.</em>"
    "</p>",
    unsafe_allow_html=True,
)
