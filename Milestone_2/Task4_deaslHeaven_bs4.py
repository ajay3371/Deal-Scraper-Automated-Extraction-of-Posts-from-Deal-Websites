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

# Function to scrape results from all stores (via the search functionality of the website)
def search_all_stores(search_query):
    search_url = f"https://dealsheaven.in?keyword={search_query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = soup.find_all('div', class_='product-item-detail')
    data = []

    for product in products:
        try:
            title = product.find('h3').get_text(strip=True)
            if search_query.lower() in title.lower():
                product_url = product.find('a')['href']
                discount = product.find('div', class_='discount').get_text(strip=True)
                price = product.find('p', class_='price').get_text(strip=True)
                special_price = product.find('p', class_='spacail-price').get_text(strip=True)
                image_url = product.find('img')['src']
                data.append({
                    'Page Number': 1,  # Dummy page number
                    'Title': title,
                    'Product URL': product_url,
                    'Discount': discount,
                    'Price': price,
                    'Special Price': special_price,
                    'Image URL': image_url,
                    'Store Name': 'All Stores'
                })
        except AttributeError:
            continue

    return data

# Function to scrape product details from a store-specific page
def scrape_store_page(store_url, page, search_query=None):
    if search_query:
        url = f"{store_url}?page={page}&keyword={search_query}"
    else:
        url = f"{store_url}?page={page}"
    
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"Failed to retrieve page {page}: Status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-item-detail')
    
    data = []
    for product in products:
        try:
            title = product.find('h3').get_text(strip=True)
            if search_query == "" or search_query.lower() in title.lower():
                product_url = product.find('a')['href']
                discount = product.find('div', class_='discount').get_text(strip=True)
                price = product.find('p', class_='price').get_text(strip=True)
                special_price = product.find('p', class_='spacail-price').get_text(strip=True)
                image_url = product.find('img')['src']
                
                data.append({
                      # Correctly set the page number
                    'Title': title,
                    'Product URL': product_url,
                    'Discount': discount,
                    'Price': price,
                    'Special Price': special_price,
                    'Image URL': image_url,
                    'Store Name': store_url.split('/')[-1]  # Extract store name from URL
                })
        except AttributeError:
            continue

    return data

# Function to find the total number of pages for a store or search query
def find_last_page(store_url):
    response = requests.get(store_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate all pagination links
    pagination = soup.select('ul.pagination li a')
    
    last_page = 1  # Default if pagination isn't found
    
    if pagination:
        page_numbers = []
        for link in pagination:
            href = link['href']
            # Extract the page number from the href
            if "page=" in href:
                page_num = href.split("page=")[-1]
                if page_num.isdigit():
                    page_numbers.append(int(page_num))
        
        if page_numbers:
            last_page = max(page_numbers)  # Set to the highest page number

    return last_page

# Function to scrape multiple pages for a specific store
def scrape_store(store, pages, search_query):
    base_url = f"https://dealsheaven.in/store/{store}"
    all_data = []

    for page in range(1, pages + 1):
        data = scrape_store_page(base_url, page, search_query)
        if data:
            all_data.extend(data)
        else:
            break  # Stop if no products found

    return all_data

# Streamlit UI
st.title("Deals Heaven Web Scraper")

# Dynamically load stores from the website
stores = get_available_stores()
if not stores:
    st.error("Could not fetch stores. Please try again later.")
else:
    store_name = st.selectbox("Select Store (Optional)", ["All Stores"] + list(stores.keys()))
    store = stores.get(store_name)

    search_query = st.text_input("Enter product to search for", "")
    
    # Display total pages available for the store
    if store_name != "All Stores":
        total_pages = find_last_page(f"https://dealsheaven.in/store/{store}")
        st.write(f"Total pages available: {total_pages}")
        pages = st.number_input("Number of Pages to Scrape", min_value=1, max_value=total_pages, step=1)
    else:
        total_pages = find_last_page("https://dealsheaven.in")
        st.write(f"Total pages available: {total_pages}")
        pages = 1  # Default for all stores

    if st.button("Scrape"):
        if store_name == "All Stores":
            scraped_data = search_all_stores(search_query)
        else:
            scraped_data = scrape_store(store, pages, search_query)

        if scraped_data:
            df = pd.DataFrame(scraped_data)
            
            required_columns = ['Store Name', 'Title', 'Product URL', 'Discount', 'Price', 'Special Price', 'Image URL']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"Missing columns in DataFrame: {missing_columns}. Please check the scraping logic.")
            else:
                df = df[required_columns]
                st.dataframe(df)

                st.success(f"Scraping completed! Data scraped from {len(scraped_data)} product(s).")
                
                # Save to CSV
                csv_file = f"{store_name}_scraped_data.csv" if store_name != "All Stores" else "all_stores_scraped_data.csv"
                df.to_csv(csv_file, index=False)
                st.success(f"Data saved to {csv_file}.")
                st.download_button(label="Download CSV", data=df.to_csv(index=False), file_name=csv_file, mime='text/csv')
        else:
            st.warning("No products found for the given search query.")
