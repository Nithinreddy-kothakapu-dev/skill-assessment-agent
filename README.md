# Skill Assessment Agent

An AI-powered agent that evaluates real skill depth through adaptive questioning and generates actionable, personalised learning paths based on performance.

## Problem Statement
A resume tells you what someone claims to know — not how well they actually know it. This agent takes a Job Description and a candidate's resume, assesses real proficiency on each required skill, identifies gaps, and generates a personalised learning plan.

## Features
- PDF resume upload and parsing
- Automatic skill extraction from JD and resume
- Skill gap detection
- AI-generated interview questions per skill
- Answer evaluation with score and confidence level
- Skill radar chart visualisation
- Personalised 2-week learning plan with free resources

## Architecture
Resume PDF + Job Description
↓
Skill Extractor (LLM)
↓
Skill Gap Detector
↓
Question Generator (LLM)
↓
Answer Evaluator (LLM)
↓
Learning Plan Generator (LLM)

## Tech Stack
- Frontend + Backend: Streamlit
- AI Model: LLaMA 3.3 70B via Groq API
- PDF Parsing: PyMuPDF
- Charts: Plotly
- Deployment: Streamlit Cloud

## How to Run
1. Clone the repo
2. Install dependencies:
   pip install -r requirements.txt
3. Add your Groq API key in app.py
4. Run:
   streamlit run app.py

## Live Demo
https://skill-assessment-agent-ebufutxxwxxijufb9ukf5j.streamlit.app/

## Sample Input
- Job Description: Python Developer role requiring Python, ML, SQL, REST APIs
- Resume: Electronics/Embedded Systems background

## Sample Output
- Skill gaps identified: Python, SQL, REST APIs, Machine Learning
- Score per skill: 0-10 with confidence level
- Personalised learning plan: Week by week with free resources
