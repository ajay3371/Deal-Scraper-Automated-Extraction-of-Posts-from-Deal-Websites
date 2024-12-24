import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Function to scrape items from Behance with search and category filtering
def scrape_behance_projects(search_term, category, max_items):
    # Define Behance URL based on category selection
    base_url = f'https://www.behance.net/assets/{category}' if category else 'https://www.behance.net/search/projects'
    driver_path = 'D:/Deal_Scrapper/edgedriver_win64/msedgedriver.exe' 
    service = Service(driver_path)
    driver = webdriver.Edge(service=service)
    driver.get(base_url)
    time.sleep(3)

    # Input search term
    if search_term:
        search_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search for assets']")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.submit()
        time.sleep(3)

    projects = []
    scroll_pause_time = 0.9

    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(projects) < max_items:
        items = driver.find_elements(By.CLASS_NAME, 'Cover-cover-gDM')
        for item in items:
            try:
                title_element = item.find_element(By.CLASS_NAME, 'Title-title-lpJ')
                owner_element = item.find_element(By.CLASS_NAME, 'Owners-overflowText-C9U')
                stats_element = item.find_element(By.CLASS_NAME, 'ProjectCover-stats-QLg')

                title = title_element.text
                owner = owner_element.text if owner_element else 'Multiple Owners'
                likes = stats_element.find_elements(By.TAG_NAME, 'span')[0].text
                views = stats_element.find_elements(By.TAG_NAME, 'span')[1].text

                projects.append({
                    'Title': title,
                    'Owner': owner,
                    'Likes': likes,
                    'Views': views
                })

                print(f"Scraped project: {title}, Owner: {owner}, Likes: {likes}, Views: {views}")

                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(scroll_pause_time)

                if len(projects) >= max_items:
                    break

            except Exception as e:
                print(f"Error extracting data: {e}")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No new content loaded, stopping.")
            break
        last_height = new_height

    driver.quit()
    return projects

# Streamlit UI
st.title("Enhanced Behance Project Scraper")
st.write("Enter search term and select category, then specify the number of projects to scrape:")

# Search term and category selection
search_term = st.text_input("Search term:")
category = st.selectbox("Select Category:", ["fonts", "templates", "vectors", "3d", "images", "videos", "icons", "brushes", "patterns"])
max_items = st.number_input("Number of items to scrape:", min_value=1, max_value=1000, value=10)

if st.button("Scrape"):
    with st.spinner("Scraping in progress..."):
        projects = scrape_behance_projects(search_term, category, max_items)
        
    if projects:
        df = pd.DataFrame(projects)
        df.index = df.index + 1
        csv_file_path = 'behance_projects.csv'
        df.to_csv(csv_file_path, index=False)
        
        st.success("Scraping completed!")
        st.write(f"Scraped {len(projects)} projects.")
        
        st.download_button("Download CSV", data=open(csv_file_path).read(), file_name='behance_projects.csv', mime='text/csv')
        st.write(df)
