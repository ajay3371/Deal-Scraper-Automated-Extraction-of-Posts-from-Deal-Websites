import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# URL of the main page
url = "https://publiclibraries.com/state/"
base_url = "https://publiclibraries.com"

# Send a request to the main page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the state links
state_links = soup.find('div', class_='dropdown-content').find_all('a')

# Create a folder to store CSVs
if not os.path.exists('states_data'):
    os.makedirs('states_data')

# Loop through each state link and scrape the state's libraries
for state in state_links:
    state_name = state.text
    state_url = state['href']

    print(f"Scraping state: {state_name} -> {state_url}")
    # Fetch the state page
    state_response = requests.get(state_url)
    state_soup = BeautifulSoup(state_response.text, 'html.parser')
    # Find the table with library information
    libraries_table = state_soup.find('table', id='libraries')
    # Debugging: Check if the table was found
    if libraries_table is None:
        print(f"No table found for {state_name}. Skipping...")
        continue  # Skip if no table found
    # Debugging: Check if tbody exists
    tbody = libraries_table.find('tbody')
    if tbody is None:
        print(f"No tbody found for {state_name}. Trying without tbody...")
        rows = libraries_table.find_all('tr')
    else:
        rows = tbody.find_all('tr')
    libraries = []
    for row in rows:
        columns = row.find_all('td')
        # Extract the data for each library, ensuring exactly 5 columns
        if len(columns) == 5: 
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
    df = pd.DataFrame(libraries)
    df.to_csv(f'states_data/{state_name}.csv', index=False)
    print(f"Data for {state_name} saved successfully.")
