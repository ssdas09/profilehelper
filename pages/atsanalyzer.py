import streamlit as st
import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
from phi.agent import Agent
from phi.assistant import Assistant
from phi.model.google import Gemini
from typing import Dict, List
import json


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def scrape_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This is a basic scraping - you might need to adjust selectors based on the target website
        job_description = soup.find('div', {'class': 'job-description'})
        return job_description.text if job_description else "Could not extract job description"
    except Exception as e:
        return f"Error scraping URL: {str(e)}"


# Define the ATS Assistant using Groq
ats_assistant = Agent(
    model=Gemini(id=f"{st.session_state['model']}",structured_outputs=True),
    name="ATS_Analyzer",
    description="An assistant that analyzes resumes against job descriptions",
    instructions=["""You are an expert ATS analyzer. Your task is to:
    1. Analyze resumes against job descriptions
    2. Calculate match percentages
    3. Identify missing keywords
    4. Provide improvement suggestions
    Always format your response as JSON with keys: 'match_percentage', 'missing_keywords', 'suggestions'"""],
    structured_outputs=True,

)


def analyze_resume(resume_text: str, job_description: str) -> Dict:
    prompt = f"""
    Analyze the following resume and job description:

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Provide:
    1. A match percentage based on skills and requirements
    2. Keywords from the job description missing in the resume
    3. Specific suggestions for improvement

    Format your response strictly as a JSON string with the following structure:
    {{
        "match_percentage": <number>,
        "missing_keywords": [<list of strings>],
        "suggestions": [<list of strings>]
    }}
    """

    # Get response from assistant and convert generator to string
    response = ""

    # st.write(ats_assistant.run(prompt).content)
    # for chunk in ats_assistant.run(prompt):
    #     response += str(chunk)

    try:
        # Parse the response string as JSON
        print(type(ats_assistant.run(prompt).content))
        print(ats_assistant.run(prompt).content.strip().removeprefix("```json").removesuffix("```").strip())
        return json.loads(ats_assistant.run(prompt).content.strip().removeprefix("```json").removesuffix("```").strip())
    except Exception as e:

        return {
            "match_percentage": 0,
            "missing_keywords": ["Error processing response"],
            "suggestions": ["Error analyzing resume and job description"]
        }


# Streamlit UI




st.title("Resume ATS Analysis Tool")
st.write("Upload your resume and provide a job description to get matching analysis")

# File upload for resume
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

# Job description input method selection
input_method = st.radio("Choose job description input method:", ["Text", "URL"])

job_description = ""
if input_method == "Text":
    job_description = st.text_area("Paste job description here:")
else:
    url = st.text_input("Enter job posting URL:")
    if url:
        job_description = scrape_job_description(url)
        st.write("Scraped Job Description:", job_description)

if uploaded_file and job_description:
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            # Extract text from resume
            resume_text = extract_text_from_pdf(uploaded_file)

            # Run the analysis
            results = analyze_resume(resume_text, job_description)

            # Display results
            st.subheader("Analysis Results")
            st.metric("Match Percentage", f"{results['match_percentage']}%")

            st.subheader("Missing Keywords")
            for keyword in results['missing_keywords']:
                st.write(f"- {keyword}")

            st.subheader("Improvement Suggestions")
            for suggestion in results['suggestions']:
                st.write(f"- {suggestion}")




