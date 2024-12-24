import streamlit as st
import pandas as pd
import requests, os, io
from bs4 import BeautifulSoup
import openpyxl

# Base URL for the state library data
main_url = "https://publiclibraries.com/state/"
base_url = "https://publiclibraries.com"

# Function to scrape the state names and URLs dynamically from the main page
def get_states():
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the dropdown containing state links
    state_elements = soup.find('div', class_='dropdown-content').find_all('a')
    
    states = {}
    for state in state_elements:
        state_name = state.text.strip()
        state_url = state['href']
        states[state_name] = state_url
    
    return states

# Function to scrape data for a specific state
def scrape_state_data(state_url):
    # Send request to state-specific page
    response = requests.get(state_url)
    
    if response.status_code != 200:
        st.error("Failed to retrieve data.")
        return pd.DataFrame()  # Return empty DataFrame in case of error
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    libraries_table = soup.find('table', id='libraries')
    
    if libraries_table is None:
        st.error("No table found for this state.")
        return pd.DataFrame()
    
    # Find rows of the table
    rows = libraries_table.find('tbody').find_all('tr') if libraries_table.find('tbody') else libraries_table.find_all('tr')
    
    # Extract the data from the table
    libraries = []
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 5:
            city = columns[0].text.strip()
            library_name = columns[1].text.strip()
            address = columns[2].text.strip()
            zip_code = columns[3].text.strip()
            phone = columns[4].text.strip()
            libraries.append({
                'City': city,
                'Library Name': library_name,
                'Address': address,
                'Zip Code': zip_code,
                'Phone': phone
            })
    
    # Return the data as a DataFrame
    return pd.DataFrame(libraries)

# Function to provide download links for different formats
def download_files(df, file_format, state_name):
    if file_format == 'CSV':
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download as CSV", data=csv, file_name=f"{state_name}.csv", mime='text/csv')
    elif file_format == 'JSON':
        json = df.to_json(orient='records').encode('utf-8')
        st.download_button(label="Download as JSON", data=json, file_name=f"{state_name}.json", mime='application/json')
    elif file_format == 'TXT':
        # Convert the DataFrame to a tab-separated string format for TXT
        txt = df.to_csv(index=False, sep='\t').encode('utf-8')
        st.download_button(label="Download as TXT", data=txt, file_name=f"{state_name}.txt", mime='text/plain')
    elif file_format == 'Excel':
        # Create an in-memory file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=state_name)
        excel_data = output.getvalue()
        st.download_button(label="Download as Excel", data=excel_data,
                           file_name=f"{state_name}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


st.markdown("# 📚 **Public Libraries Data**")
st.markdown("#### download and view public library data by state")
st.markdown("---")

# Scrape state names and URLs dynamically
states = get_states()

# Dropdown to select a state
state_name = st.selectbox("Select a state to scrape library data", list(states.keys()))

# When the state is selected, scrape the data
if state_name:
    state_url = states[state_name]
    state_data = scrape_state_data(state_url)
    
    if not state_data.empty:
        st.markdown(f"### 📖 **Library Data for {state_name}**")
        state_data.index = state_data.index + 1
        st.dataframe(state_data, use_container_width=True)
        
        # Provide download options inside an expander
        with st.expander("Download options"):
            col1, col2, col3,col4 = st.columns(4)
            with col1:
                download_files(state_data, 'CSV', state_name)
            with col2:
                download_files(state_data, 'JSON', state_name)
            with col3:
                download_files(state_data,'TXT',state_name)
            with col4:
                download_files(state_data, 'Excel', state_name)
    else:
        st.write(f"No data available for {state_name}.")