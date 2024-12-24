import os
import streamlit as st
from streamlit_tags import st_tags
from scraper import scrape_and_convert
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Universal Web Scraper", layout="wide")

# Apply custom CSS for UI
st.markdown("""
    <style>
    .title {
        font-size: 2.6em;  
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
        font-family: 'Arial', sans-serif;
    }
    .icon {
        font-size: 0.9em;  
        color: #ff007f;
        display: inline-block;  
        transform: rotate(40deg);
    }
    .separator {
        margin-top: 20px;
        border-top: 1px solid #666; 
    }
    .button-container {
        margin-top: 30px;  
        text-align: center;  
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<div class="title">Universal Web Scraper 🦑</div>', unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.header("Scraper Settings")
    model_choice = st.selectbox("Select Model", ["gpt-4", "gemini-flash"])
    url = st.text_input("Enter URL")
    
    # Field selection
    fields = st_tags(label="Fields to Extract:", text="Add fields", value=[], maxtags=20, key="fields_input")

    # Scrape button
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.write("")
    scrape_button = st.button("Scrape")
    
# Display table only when button is pressed
if scrape_button:
    if not url:
        st.warning("Please enter a URL.")
    else:
        # Call perform_scrape with selected parameters
        fields_list = st.session_state['fields_input']
        result = scrape_and_convert(url, fields_list, model_choice)
        
        if result and 'table' in result:
            st.success("Data extracted successfully!")
            st.dataframe(result['table'])  # Display data in table format

            # Ensure 'output' directory exists
            os.makedirs("output", exist_ok=True)

            # Generate timestamped CSV filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"output/extracted_data_{timestamp}.csv"

            # Save table as CSV to 'output' folder
            result['table'].to_csv(csv_filename, index=False)

            # Provide a download button for CSV
            with open(csv_filename, "rb") as file:
                st.download_button(
                    label="Download CSV",
                    data=file,
                    file_name=f"extracted_data_{timestamp}.csv",
                    mime="text/csv"
                )
        else:
            st.error("Failed to retrieve data in the expected format.")
