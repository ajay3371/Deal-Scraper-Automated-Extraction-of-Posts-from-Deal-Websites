import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Initialize WebDriver
def initialize_driver():
    driver_path = 'D:\\Deal_Scrapper\\edgedriver_win64\\msedgedriver.exe'
    service = Service(driver_path)
    driver = webdriver.Edge(service=service)
    return driver

# Fetch categories for Assets and Jobs
@st.cache_data(show_spinner=False)
def fetch_categories(category):
    driver = initialize_driver()
    url = "https://www.behance.net/assets" if category == "Assets" else "https://www.behance.net/joblist"
    driver.get(url)
    time.sleep(3)

    categories = []
    try:
        if category == "Assets":
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.AssetsFilterAccordion-accordionSection-RNi a'))
            )
            elements = driver.find_elements(By.CSS_SELECTOR, 'div.AssetsFilterAccordion-accordionSection-RNi a')
            for element in elements:
                subcategory_name = element.text
                subcategory_path = element.get_attribute('href')
                categories.append((subcategory_name, subcategory_path))
        else:
            # Fetch main job categories
            main_category_elements = driver.find_elements(By.CSS_SELECTOR, 'fieldset.CategoryFilter-fieldset-o7r .Radio-container-lLR')
            for main_element in main_category_elements:
                subcategory_name = main_element.find_element(By.TAG_NAME, 'span').text
                subcategory_id = main_element.find_element(By.TAG_NAME, 'input').get_attribute('id')
                categories.append((subcategory_name, subcategory_id))
    except Exception as e:
        print(f"Error fetching categories: {e}")
    driver.quit()
    return categories

# Scrape Asset projects based on URL and keyword
def scrape_assets(url, max_items, keyword):
    driver = initialize_driver()
    search_url = f"{url}?search={keyword}"
    driver.get(search_url)
    time.sleep(3)

    projects = []
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(projects) < max_items:
        items = driver.find_elements(By.CLASS_NAME, 'Cover-cover-gDM')
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, 'Title-title-lpJ').text
                owner = item.find_element(By.CLASS_NAME, 'Owners-overflowText-C9U').text
                stats = item.find_element(By.CLASS_NAME, 'ProjectCover-stats-QLg')
                likes = stats.find_elements(By.TAG_NAME, 'span')[0].text
                views = stats.find_elements(By.TAG_NAME, 'span')[1].text
                projects.append({
                    'Title': title,
                    'Owner': owner,
                    'Likes': likes,
                    'Views': views
                })
                driver.execute_script("window.scrollBy(0, 100);")
                time.sleep(scroll_pause_time)

                if len(projects) >= max_items:
                    break
            except Exception as e:
                print(f"Error extracting asset data: {e}")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return projects

# Scrape Job listings based on selected category and keyword
def scrape_jobs(category_id, max_items, keyword):
    driver = initialize_driver()
    search_url = f"https://www.behance.net/joblist?search={keyword}&category={category_id}"
    driver.get(search_url)
    time.sleep(3)

    jobs = []
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(jobs) < max_items:
        items = driver.find_elements(By.CLASS_NAME, 'JobCard-jobCard-mzZ')
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, 'JobCard-jobTitle-LS4').text
                company = item.find_element(By.CLASS_NAME, 'JobCard-company-GQS').text
                location = item.find_element(By.CLASS_NAME, 'JobCard-jobLocation-sjd').text
                posted = item.find_element(By.CLASS_NAME, 'JobCard-time-Cvz').text
                description = item.find_element(By.CLASS_NAME, 'JobCard-jobDescription-SYp').text
                jobs.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Posted': posted,
                    'Description': description
                })
                driver.execute_script("window.scrollBy(0, 100);")
                time.sleep(scroll_pause_time)

                if len(jobs) >= max_items:
                    break
            except Exception as e:
                print(f"Error extracting job data: {e}")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return jobs

# Streamlit UI
st.title("Behance Scraper")
st.write("Select the category, enter the number of items to scrape, and an optional search keyword:")

# Category selection
category = st.selectbox("Choose a category:", ("Assets", "Jobs"), index=0)
categories = fetch_categories(category)

if categories:
    category_names = [name for name, _ in categories]
    selected_category_name = st.selectbox("Choose a subcategory:", category_names)
    selected_category_path = next(path for name, path in categories if name == selected_category_name)

    keyword = st.text_input("Enter a search keyword:", "")
    max_items = st.number_input("Number of items to scrape:", min_value=1, max_value=1000, value=10)

    if category == "Jobs":
        print(selected_category_name.lower().replace(' ','-'))
        if st.button("Scrape"):
            with st.spinner("Scraping in progress..."):
                print(selected_category_name)
                results = scrape_jobs(selected_category_name.lower().replace(' ','-'), max_items, keyword)  # Use category ID

            if results:
                df = pd.DataFrame(results)
                df.index=df.index+1
                csv_file_path = 'behance_jobs_data.csv'
                df.to_csv(csv_file_path, index=False)
                st.success(f"Scraping completed! Scraped {len(results)} job items.")
                st.write(df)
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    csv_data = file.read()
                st.download_button("Download CSV", data=csv_data, file_name='behance_jobs_data.csv', mime='text/csv')
    else:
        if st.button("Scrape"):
            with st.spinner("Scraping in progress..."):
                results = scrape_assets(selected_category_path, max_items, keyword)  # Use subcategory URL

            if results:
                df = pd.DataFrame(results)
                df.index=df.index+1
                csv_file_path = 'behance_assets_data.csv'
                df.to_csv(csv_file_path, index=False)
                st.success(f"Scraping completed! Scraped {len(results)} asset items.")
                st.write(df)
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    csv_data = file.read()
                st.download_button("Download CSV", data=csv_data, file_name='behance_assets_data.csv', mime='text/csv')
else:
    st.warning("No categories found.")
