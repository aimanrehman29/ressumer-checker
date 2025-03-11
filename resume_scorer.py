import google.generativeai as genai
import PyPDF2
import docx2txt
import spacy
import streamlit as st
import spacy
import subprocess
import os

# Check if spaCy model is installed, if not, install it
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
    
genai.configure(api_key="AIzaSyDcSBiArvRkffjtK_izwZtxBCdEP31R50k")

def extract_text_from_resume(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)
    else:
        return None

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return ", ".join(set(keywords)) 

def compare_resume_with_job_description(resume_text, job_description):
    prompt = f"""
    You are an AI resume evaluator. Compare the resume with the job description 
    and provide a matching score (0-100%) along with improvement suggestions.

    **Resume Content:** {resume_text}

    **Job Description:** {job_description}

    Provide output in this format:
    - Matching Score: XX%
    - Strengths: (mention positive points)
    - Weaknesses: (mention areas for improvement)
    """
    
    model = genai.GenerativeModel("gemini-2.0-flash") 
    response = model.generate_content(prompt)

    return response.text 


st.title("📄 AI-Powered Resume Scorer ")


uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])

job_description = st.text_area("Paste Job Description Here")

if uploaded_file and job_description:
    with st.spinner("Analyzing..."):
        resume_text = extract_text_from_resume(uploaded_file)
        if resume_text:
            keywords = extract_keywords(resume_text)
            st.subheader("🔍 Extracted Resume Keywords")
            st.write(keywords)

           
            result = compare_resume_with_job_description(resume_text, job_description)
            st.subheader("🎯 AI Resume Score & Feedback")
            st.write(result)
        else:
            st.error("Error extracting text. Please upload a valid resume file.")
