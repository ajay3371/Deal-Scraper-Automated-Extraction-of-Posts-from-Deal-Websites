import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time

# Function to initialize Edge WebDriver
def init_driver():
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    edge_options.add_argument("--window-size=1920,1080")
    
    # Set the path to your msedgedriver.exe here manually
    driver_path = 'D:/Deal_Scrapper/edgedriver_win64/msedgedriver.exe'
    
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    
    return driver

# Function to fetch available stores dynamically using Selenium
def get_available_stores(driver):
    url = "https://dealsheaven.in/stores"
    driver.get(url)
    time.sleep(2)

    stores = {}
    store_links = driver.find_elements(By.CSS_SELECTOR, 'ul > li > a[href^="https://dealsheaven.in/store/"]')
    
    for store in store_links:
        store_name = store.text.strip()
        store_url = store.get_attribute('href')
        store_key = store_url.split('/')[-1]
        stores[store_name] = store_key
    
    return stores

# Function to scrape product details from a store-specific page using Selenium
def scrape_store_page(driver, store_url, page, search_query=None):
    if search_query:
        url = f"{store_url}?page={page}&keyword={search_query}"
    else:
        url = f"{store_url}?page={page}"

    driver.get(url)
    time.sleep(2)

    products = driver.find_elements(By.CLASS_NAME, 'product-item-detail')
    
    data = []
    for product in products:
        try:
            title = product.find_element(By.TAG_NAME, 'h3').text.strip()
            product_url = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
            discount = product.find_element(By.CLASS_NAME, 'discount').text.strip()
            price = product.find_element(By.CLASS_NAME, 'price').text.strip()
            special_price = product.find_element(By.CLASS_NAME, 'spacail-price').text.strip()
            image_url = product.find_element(By.TAG_NAME, 'img').get_attribute('src')
            
            data.append({
                'Title': title,
                'Product URL': product_url,
                'Discount': discount,
                'Price': price,
                'Special Price': special_price,
                'Image URL': image_url,
                'Store Name': store_url.split('/')[-1]  # Extract store name from URL
            })
        except Exception:
            continue

    return data

# Function to find the total number of pages for a store using Selenium
def find_last_page(driver, store_url):
    driver.get(store_url)
    time.sleep(2)

    pagination = driver.find_elements(By.CSS_SELECTOR, 'ul.pagination li a')
    
    last_page = 1  # Default if pagination isn't found
    
    if pagination:
        page_numbers = []
        for link in pagination:
            href = link.get_attribute('href')
            if "page=" in href:
                page_num = href.split("page=")[-1]
                if page_num.isdigit():
                    page_numbers.append(int(page_num))
        
        if page_numbers:
            last_page = max(page_numbers)  # Set to the highest page number

    return last_page

# Function to scrape multiple pages for a specific store
def scrape_store(driver, store, pages, search_query):
    base_url = f"https://dealsheaven.in/store/{store}"
    all_data = []

    # Navigate and scrape when scraping is triggered
    for page in range(1, pages + 1):
        data = scrape_store_page(driver, base_url, page, search_query)
        if data:
            all_data.extend(data)
        else:
            break  # Stop if no products found

    return all_data

# Streamlit UI
st.title("Deals Heaven Web Scraper with Selenium")

# Initialize WebDriver (Edge) and load stores automatically when the app starts
driver = init_driver()
stores = get_available_stores(driver)

if not stores:
    st.error("Could not fetch stores. Please try again later.")
else:
    store_name = st.selectbox("Select Store", list(stores.keys()))
    store = stores.get(store_name)

    # Automatically fetch total pages when a store is selected
    if store_name:  
        # Fetch total pages only when the store is selected
        total_pages = find_last_page(driver, f"https://dealsheaven.in/store/{store}")
        st.write(f"Total pages available: {total_pages}")

        # Display number input for pages and search query text input
        pages = st.number_input("Number of Pages to Scrape", min_value=1, max_value=total_pages, step=1)
        search_query = st.text_input("Enter product to search for", "")
        
        # Scrape only when the button is clicked
        if st.button("Scrape"):
            scraped_data = scrape_store(driver, store, pages, search_query)

            if scraped_data:
                df = pd.DataFrame(scraped_data)
                st.dataframe(df)

                # Save to CSV
                csv_file = f"{store_name}_scraped_data.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Data saved to {csv_file}.")
                st.download_button(label="Download CSV", data=df.to_csv(index=False), file_name=csv_file, mime='text/csv')
            else:
                st.warning("No products found for the given search query.")

# Close the driver after scraping
driver.quit()
