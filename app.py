import streamlit as st
from groq import Groq
import pymupdf
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key="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")

def extract_text_from_pdf(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_skills(text, source):
    prompt = f"""
    Extract only the technical skills from this {source}.
    Return ONLY a comma separated list. No explanation.
    Example: Python, Machine Learning, SQL
    Text: {text}
    """
    result = ask_groq(prompt)
    skills = [s.strip() for s in result.split(",") if s.strip()]
    return skills

def generate_question(skill, level="medium"):
    prompt = f"""
    Generate ONE interview question to test {skill} at {level} difficulty.
    Return ONLY the question. Nothing else.
    """
    return ask_groq(prompt)

def evaluate_answer(skill, question, answer):
    prompt = f"""
    Evaluate this interview answer for the skill: {skill}
    Question: {question}
    Answer: {answer}
    Return EXACTLY in this format:
    Score: X/10
    Confidence: High/Medium/Low
    Feedback: one sentence feedback
    """
    return ask_groq(prompt)

def generate_learning_plan(skill, score):
    prompt = f"""
    Create a 2 week learning plan for {skill}.
    The candidate scored {score}/10.
    Return in this format:
    Week 1: topic to study
    Week 2: topic to study
    Resources: 2-3 free online resources
    Time: estimated hours per day
    """
    return ask_groq(prompt)

def create_radar_chart(skills, scores):
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=skills,
        fill='toself',
        fillcolor='rgba(83, 74, 183, 0.2)',
        line=dict(color='rgb(83, 74, 183)')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        title="Skill Radar Chart",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# ---- CUSTOM CSS ----
st.set_page_config(page_title="Skill Assessment Agent", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 15px;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 16px;
        font-weight: 600;
        color: #1a1a2e;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 6px;
        border-bottom: 1.5px solid #534AB7;
        display: inline-block;
    }
    .skill-card {
        background: #f8f8ff;
        border: 1px solid #e0deff;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }
    .stat-box {
        background: #f4f4f8;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        font-size: 13px;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888;
        margin-bottom: 4px;
    }
    .plan-item {
        background: #EEEDFE;
        border-left: 3px solid #534AB7;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 14px;
        color: #3C3489;
    }
    .stButton > button {
        background-color: #534AB7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #3C3489;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown('<div class="main-title">Skill Assessment Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload your resume and job description — get assessed with a personalised learning plan</div>', unsafe_allow_html=True)

# ---- INPUT SECTION ----
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Your Resume</div>', unsafe_allow_html=True)
    st.write("")
    resume_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)
    st.write("")
    jd_text = st.text_area("Paste job description", height=160, label_visibility="collapsed", placeholder="Paste the job description here...")

st.write("")
if st.button("Start Assessment", use_container_width=True):
    if not resume_file or not jd_text:
        st.error("Please upload your resume and paste the job description!")
    else:
        with st.spinner("Reading your resume..."):
            resume_text = extract_text_from_pdf(resume_file)
            st.session_state.resume_text = resume_text

        with st.spinner("Extracting and comparing skills..."):
            jd_skills = extract_skills(jd_text, "job description")
            resume_skills = extract_skills(resume_text, "resume")
            gap_skills = list(set(jd_skills) - set(resume_skills))

            st.session_state.jd_skills = jd_skills
            st.session_state.resume_skills = resume_skills
            st.session_state.gap_skills = gap_skills
            st.session_state.assessment_started = True
            st.session_state.current_skill_index = 0
            st.session_state.scores = {}
            st.session_state.questions = {}
            st.session_state.feedbacks = {}

# ---- RESULTS SECTION ----
if st.session_state.get("assessment_started"):
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">JD Skills</div>
            <div>{', '.join(st.session_state.jd_skills[:5])}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Your Skills</div>
            <div>{', '.join(st.session_state.resume_skills[:5])}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label" style="color:#A32D2D;">Skill Gaps</div>
            <div style="color:#A32D2D;">{', '.join(st.session_state.gap_skills[:5])}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-header">Skill Assessment</div>', unsafe_allow_html=True)
    st.write("")

    skills_to_assess = st.session_state.jd_skills[:4]

    for i, skill in enumerate(skills_to_assess):
        with st.expander(f"Skill {i+1}: {skill}", expanded=(i == st.session_state.current_skill_index)):
            if skill not in st.session_state.questions:
                with st.spinner(f"Generating question for {skill}..."):
                    q = generate_question(skill)
                    st.session_state.questions[skill] = q

            st.markdown(f"**Question:** {st.session_state.questions[skill]}")
            answer = st.text_area(f"Your answer", key=f"ans_{skill}", placeholder="Type your answer here...")

            if st.button(f"Submit answer", key=f"btn_{skill}"):
                if answer:
                    with st.spinner("Evaluating..."):
                        result = evaluate_answer(skill, st.session_state.questions[skill], answer)
                        st.session_state.feedbacks[skill] = result
                        lines = result.split("\n")
                        score = 5
                        for line in lines:
                            if "Score:" in line:
                                try:
                                    score = int(line.split(":")[1].strip().split("/")[0])
                                except:
                                    score = 5
                        st.session_state.scores[skill] = score
                        st.session_state.current_skill_index = i + 1

            if skill in st.session_state.feedbacks:
                st.markdown('<div class="plan-item">' + st.session_state.feedbacks[skill].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)

    if len(st.session_state.scores) == len(skills_to_assess):
        st.write("")
        st.markdown('<div class="section-header">Skill Radar Chart</div>', unsafe_allow_html=True)
        st.write("")
        skills_list = list(st.session_state.scores.keys())
        scores_list = list(st.session_state.scores.values())
        fig = create_radar_chart(skills_list, scores_list)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">Personalised Learning Plan</div>', unsafe_allow_html=True)
        st.write("")
        for skill, score in st.session_state.scores.items():
            with st.expander(f"{skill}  —  Score: {score}/10"):
                with st.spinner(f"Generating plan for {skill}..."):
                    plan = generate_learning_plan(skill, score)
                    st.markdown('<div class="plan-item">' + plan.replace("\n", "<br>") + '</div>', unsafe_allow_html=True)