from Task6_Behance_Modular import run_behance
from Task6_Deals_Heaven_Modular import run_DealsHeaven
import streamlit as st
options = ["Select an option", "Behance", "Deals_Heaven",]
st.title("Web Scraper for Behance and Deals Heaven")
selected_option = st.sidebar.selectbox("Choose an option", options)
if selected_option.lower() == "Behance".lower():
    run_behance()
    st.write("Running Behance...")   
elif selected_option == "Deals_Heaven":
    st.write("Running Deals Heaven...")
    run_DealsHeaven()
else:
    st.write("Please select an option to run.")
