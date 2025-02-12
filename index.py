import streamlit as st
import os

st.title("Job Search helper")

st.subheader("Enter your gemini api key to get started")

api_key = st.text_input("Enter your Gemini API Key", type="password")
models = ["gemini-pro", "gemini-2.0-flash"]  # Add more if needed
selected_model = st.selectbox("Choose a Gemini Model", models)
st.session_state['model'] = selected_model
# Set API Key as an environment variable
if api_key and 'model' in st.session_state:
    os.environ["GOOGLE_API_KEY"] = api_key

    st.success("API Key Set Successfully!")
else:
    st.warning("Please enter a valid API Key.")

# Gemini Model Selection




