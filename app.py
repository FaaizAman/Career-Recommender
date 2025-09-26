import streamlit as st
import pickle
import numpy as np
from collections import defaultdict

# ---------- Load Model & Imputer ----------
@st.cache_resource
def load_model_imputer():
    with open("career_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("imputer.pkl", "rb") as f:
        imputer = pickle.load(f)
    with open("career_mapping.pkl", "rb") as f:
        career_mapping = pickle.load(f)
    return model, imputer, career_mapping

career_model, imputer, career_mapping = load_model_imputer()


# ---------- CSS ----------
st.markdown("""
<style>
    .header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .career-card {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: #ffffff;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #6e48aa;
    }
    .group-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #9d50bb;
        margin-top: 2rem;
    }
    .threshold {
        font-size: 0.9rem;
        background: #ff6b6b;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Set the page config with title and favicon
st.set_page_config(
    page_title="Career Recommender",
    # page_icon="",
    layout="centered"
)

# ---------- Header ----------
st.markdown("""
<div class="header">
    <h1>Career Recommender</h1>
    <p>Get personalized career recommendations based on your academic performance</p>
</div>
""", unsafe_allow_html=True)

# ---------- Input Form ----------
with st.form("career_form"):
    name = st.text_input("Your Name")
    col1, col2 = st.columns(2)
    with col1:
        math = st.slider("Math", 0, 100, 75)
        physics = st.slider("Physics", 0, 100, 70)
        chemistry = st.slider("Chemistry", 0, 100, 65)
        biology = st.slider("Biology", 0, 100, 75)
    with col2:
        english = st.slider("English", 0, 100, 80)
        history = st.slider("History", 0, 100, 70)
        geography = st.slider("Geography", 0, 100, 70)
        study_hours = st.slider("Weekly Study Hours", 0, 50, 15)

    submit = st.form_submit_button("Get Recommendations")

# ---------- On Submit ----------
user_scores = {
        "math_score": math,
        "physics_score": physics,
        "chemistry_score": chemistry,
        "biology_score": biology,
        "english_score": english,
        "history_score": history,
        "geography_score": geography,
        "weekly_self_study_hours": study_hours
    }
if submit:

    # Predict group using model
    user_array = np.array([[math, physics, chemistry, biology,
                            english, history, geography, study_hours]])
    user_array_imputed = imputer.transform(user_array)
    predicted_group = career_model.predict(user_array_imputed)[0]

    # Check all qualified careers
    qualified = []
    for career, data in career_mapping.items():
        weights = data["weights"]
        threshold = data["threshold"]
        total = sum(user_scores.get(k, 0) * v for k, v in weights.items())
        weight_sum = sum(weights.values())
        score = (total / weight_sum) if weight_sum > 0 else 0

        if score >= threshold:
            qualified.append({
                "name": career,
                "group": data["group"],
                "score": round(score, 2),
                "threshold": threshold,
                "description": data["description"]
            })

    if not qualified:
        st.warning("No careers matched your profile. Improve scores to unlock more.")
    else:
        # Hybrid logic: if 10+ qualified careers → group-based top 5, else top 5 overall
        # Always show top 5 overall careers based on score
        top_careers = sorted(qualified, key=lambda x: x["score"], reverse=True)[:5]

        num_recommended = len(qualified)
        if num_recommended == 1:
            st.markdown(f"Here is your recommended career:")
        elif num_recommended <= 5 :
            st.markdown(f"Here are your top {num_recommended} recommended careers:")
        else:
            st.markdown(f"Here are your top 5 recommended careers:")

        for c in top_careers:
            st.markdown(f"""
            <div class="career-card">
                <h4>{c['name']} ({c['group']})</h4>
                <p>{c['description']}</p>
                <small>Score: {c['score']}% | Required: {c['threshold']}%</small>
            </div>
            """, unsafe_allow_html=True)


improvement_tips = {
    "math_score": "Practice algebra, geometry, and calculus regularly. Use apps like Khan Academy or Cuemath.",
    "physics_score": "Focus on problem-solving and understanding core concepts. Use visual simulations.",
    "chemistry_score": "Revise reaction mechanisms and periodic table trends. Practice with previous year questions.",
    "biology_score": "Review diagrams and processes. Focus on NCERT and concept-based questions.",
    "english_score": "Improve vocabulary, reading comprehension, and writing. Read editorials and practice grammar.",
    "history_score": "Create timelines and understand cause-effect of events. Use flashcards for dates.",
    "geography_score": "Study maps, physical processes, and current affairs. Practice with past questions.",
    "weekly_self_study_hours": "Try to increase dedicated study hours gradually by creating a daily routine."
}

# Identify weak areas (less than 60%) or low study hours
weak_subjects = []

for subj, score in user_scores.items():
    if subj == "weekly_self_study_hours":
        if score < 25:
            weak_subjects.append(subj)
    elif score < 60:
        weak_subjects.append(subj)

# Display improvement tips
if weak_subjects:
    st.subheader("Suggested Improvement Areas")
    for subject in weak_subjects:
        tip = improvement_tips.get(subject)
        formatted_subject = subject.replace("_score", "").replace("_", " ").capitalize()
        if tip:
            st.markdown(f"**{formatted_subject}**: {tip}")

