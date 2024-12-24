import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Function to fetch the available stores dynamically
def get_available_stores():
    url = "https://dealsheaven.in/stores"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    stores = {}
    store_links = soup.select('ul > li > a[href^="https://dealsheaven.in/store/"]')
    
    for store in store_links:
        store_name = store.get_text(strip=True)
        store_url = store['href']
        store_key = store_url.split('/')[-1]
        stores[store_name] = store_key
    
    return stores

# Function to find the last page dynamically
def find_last_page(store_url):
    response = requests.get(store_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    last_page = 1  # Default if pagination is not found
    pagination = soup.select('ul.pagination li.page-item a.page-link')
    
    if pagination:
        try:
            # Extract the last page number (ignoring "..." and non-page links)
            for link in pagination:
                page_num = link.get_text(strip=True)
                if page_num.isdigit():
                    last_page = int(page_num)
        except (ValueError, IndexError):
            last_page = 1  # Fallback if there's any issue
    
    return last_page

# Function to scrape product details from a single page
def scrape_store_page(store_url, page):
    url = f"{store_url}?page={page}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-item-detail')

    data = []
    for product in products:
        try:
            title = product.find('h3').get_text(strip=True)
            product_url = product.find('a')['href']
            discount = product.find('div', class_='discount').get_text(strip=True)
            price = product.find('p', class_='price').get_text(strip=True)
            special_price = product.find('p', class_='spacail-price').get_text(strip=True)
            image_url = product.find('img')['src']
            data.append({
                'Title': title,
                'Product URL': product_url,
                'Discount': discount,
                'Price': price,
                'Special Price': special_price,
                'Image URL': image_url
            })
        except AttributeError:
            continue  # If any product data is missing, skip it
    return data

# Function to scrape multiple pages based on user input
def scrape_store(store, pages):
    base_url = f"https://dealsheaven.in/store/{store}"
    all_data = []

    for page in range(1, pages + 1):
        data = scrape_store_page(base_url, page)
        if data:
            all_data.extend(data)
        else:
            st.error(f"Page {page} does not exist!")
            break  # Stop if the page doesn't exist

    return all_data

# Streamlit UI
st.title("Deals Heaven Web Scraper")

# Dynamically load stores from the website
stores = get_available_stores()
if not stores:
    st.error("Could not fetch stores. Please try again later.")
else:
    # User input for store and number of pages
    store_name = st.selectbox("Select Store", list(stores.keys()))
    store = stores[store_name]

    # Find the last page dynamically
    last_page = find_last_page(f"https://dealsheaven.in/store/{store}")
    st.write(f"Max pages available for {store_name}: {last_page}")

    # Input number of pages, no limits but handle validation later
    pages = st.number_input("Number of Pages to Scrape", min_value=1, step=1)

    # Scrape data when the button is clicked
    if st.button("Scrape"):
        # Validate if the entered number of pages is greater than the last page
        if pages > last_page:
            st.error(f"Only {last_page} pages exist. Please input a number between 1 and {last_page}.")
        else:
            scraped_data = scrape_store(store, pages)
            if scraped_data:
                df = pd.DataFrame(scraped_data)
                st.dataframe(df)  # Display scraped data in the UI
                
                # Save to CSV
                csv_file = f"{store}_scraped_data.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Scraping completed! Data saved to {csv_file}.")
                st.download_button(label="Download CSV", data=df.to_csv(index=False), file_name=csv_file, mime='text/csv')
