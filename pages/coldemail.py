
import streamlit as st
import os
from phi.agent import Agent
from phi.tools.email import EmailTools
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import PyPDF2
from mailer import send_email
import json


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def main():
    st.title("Smart Resume Email Composer")

    # File upload for resume
    uploaded_resume = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])
    # resume_text = extract_text_from_pdf(uploaded_resume)
    if uploaded_resume:
        # Save the uploaded resume temporarily
        with open(f"{uploaded_resume.name}", "wb") as f:
            f.write(uploaded_resume.getbuffer())

        st.success("Resume uploaded successfully!")

        # Get email configuration
        st.subheader("Email Configuration")
        receiver_email = st.text_input("Recruiter's Email")
        job_role = st.text_input("Job Role")
        company_name = st.text_input("Company Name")
        sender_email = st.text_input("Your Email")
        sender_name = st.text_input("Your Name")
        sender_passkey = st.text_input("Your Email App Password", type="password",
                                       help="Use app-specific password for Gmail")
        phone_number = st.text_input("Enter mobile number")
        linkedin_profile = st.text_input("enter linkeding url")
        github_profile = st.text_input("enter github_url")


        if all([receiver_email, company_name, sender_email, sender_name, sender_passkey]):
            # Initialize AI agent with email tools
            resume_text=extract_text_from_pdf(uploaded_resume)
            agent = Agent(
                model=Gemini(id=f"{st.session_state['model']}", structured_outputs=True),
                instructions=[
                    """
                    You are an expert in composing job aplication emails and do not send email
                    """
                ],
                tools=[DuckDuckGo(),
                    EmailTools(
                        receiver_email=receiver_email,
                        sender_email=sender_email,
                        sender_name=sender_name,
                        sender_passkey=sender_passkey,
                    )
                ]

            )

            # Compose initial email
            if st.button("Compose Email"):
                prompt = f"""
                Analyze the following resume and job description:

                Resume:
                {resume_text}
                
                Then based on my resume compose a professional job application email with the following details:
                - Company: {company_name}
                - Job Role: {job_role}
                - Use a formal tone
                - Show my skills and achievements in bullet points
                - Mention interest in potential opportunities
                - Reference the attached resume
                - mention my profile details {phone_number},{linkedin_profile},{github_profile}
                
                Provide:
                1. An eye catching subject 
                2. An engaing mail body
            
                Format your response strictly as a JSON string with the following structure:
                {{
                    "subject": <string in capital>,
                    "body": <200 words email body highlighting my strengths,include bullet points>
                }}
                """
                composed_email = agent.run(prompt).content.strip().removeprefix("```json").removesuffix("```").strip()
                st.session_state.email_content = composed_email
                st.text_area("Composed Email", composed_email, height=300, key="email_display")

            # Rewrite option
            if 'email_content' in st.session_state and st.button("Ask AI to Rewrite"):
                rewrite_prompt = f"Rewrite the previous email to make it more compelling and professional while maintaining the same information based on previous respose you generated {st.session_state.email_content}"
                rewritten_email = agent.run(rewrite_prompt).content.strip().removeprefix("```json").removesuffix("```").strip()
                st.session_state.email_content = rewritten_email
                st.text_area("Rewritten Email", rewritten_email, height=300, key="rewritten_display")

            # Send email
            if 'email_content' in st.session_state and st.button("Send Email"):
                email = json.loads(st.session_state.email_content)
                try:
                    send_email(
                        gmail_user=sender_email,
                        to_email=receiver_email,
                        subject=email['subject'],
                        body=email['body'],
                        password=sender_passkey,
                        PDF_PATH=uploaded_resume.name
                    )
                    st.success("Email sent successfully!")

                    # Clean up
                    os.remove(f"{uploaded_resume.name}")

                except Exception as e:
                    st.error(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    main()


