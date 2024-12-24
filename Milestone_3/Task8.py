import streamlit as st
from streamlit_tags import st_tags
st.set_page_config(page_title="Universal Web Scraper", layout="wide")

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

st.markdown('<div class="title">Universal Web Scraper <span class="icon">🦑</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Web Scraper Settings")
    model_choice = st.selectbox("Select Model", ["gpt-4o", "gemini-1.5-flash"])
    
    url = st.text_input("Enter URL")
    
    # Tag-style input for fields to extract
    fields = st_tags(
        label="Enter Fields to Extract:",
        text="Press enter to add more fields",
        value=[], 
        maxtags=20, 
        key="fields_input"
    )
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("Scrape"):
        if not url:
            st.warning("Please enter a URL.")
        else:
            st.success("Scraping started!")
    st.markdown('</div>', unsafe_allow_html=True)
