import os
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

# Get the API key from the environment variables
api_key = os.getenv("API_KEY")
# Configure Google Generative AI with the API key
genai.configure(api_key)
def generate_ai_content(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

st.title("AI Content Generator")
st.subheader("AI Content Generation")
ai_prompt = st.text_input("Enter a prompt for AI content:")
if st.button("Generate AI Content"):
    if ai_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating content..."):
            ai_response = generate_ai_content(ai_prompt)
        st.text_area("AI Response", value=ai_response, height=300)


