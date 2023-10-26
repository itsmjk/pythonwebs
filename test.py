from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
import time

# Function to fetch deals based on a merchant name
def fetch_deals(merchant_name=""):
    # Start a headless Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # The URL of the web page
    url = "https://www.hotukdeals.com/deals-new"
    driver.get(url)

    # Wait for the page to load (you might need to adjust the duration)
    time.sleep(5)

    # Get the page source after dynamic content has loaded
    page_source = driver.page_source
    driver.quit()

    # Parse the HTML content of the page
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all product articles
    product_articles = soup.find_all("article", class_="thread")

    # Extract and print the URL with the 7-digit code, title, and price for each product
    for article in product_articles:
        temp_element = article.find("span", class_="cept-vote-temp")
        if temp_element:
            temp_text = temp_element.text.strip()
            if temp_text.endswith("°") and int(temp_text[:-1]) > 25:
                data_t = article.get("data-t-d")
                if data_t:
                    try:
                        data = json.loads(data_t)
                        code = data.get("id", "Code not available")
                        title = article.find("a", class_="cept-tt").text
                        price_element = article.find("span", class_="thread-price")
                        price = price_element.text.strip() if price_element else "Price not available"
                        merchant = article.find("span", class_="cept-merchant-name text--b text--color-brandPrimary link")

                        if not merchant_name or (merchant and merchant.text.strip().lower() == merchant_name.lower()):
                            deal_url = f"https://www.hotukdeals.com/visit/homeyou/{code}"

                            # Send an additional GET request to the URL to follow redirection
                            response = requests.get(deal_url, timeout=10)  # Add a timeout of 10 seconds
                            print(response)
                            
                            if response.status_code == 503:
                                # Use the URL after redirection
                                final_url = response.url
                                print(f"7-digit code: {code}")
                                print(f"Title: {title}")
                                print(f"Price: {price}")
                                print(f"URL: {final_url}")
                                print(f"Temperature: {temp_text}")
                                print()
                            elif response.status_code == 200:
                                # Use the URL after redirection
                                final_url = response.url
                                print(f"7-digit code: {code}")
                                print(f"Title: {title}")
                                print(f"Price: {price}")
                                print(f"URL: {final_url}")
                                print(f"Temperature: {temp_text}")
                                print()
                            else:
                                print(f"Failed to fetch the deal URL: {deal_url}")
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                        continue  # Continue to the next deal

# Input your desired merchant name or leave it empty to fetch all deals
# Example: merchant_name = "Amazon" or merchant_name = ""
merchant_name = ""
fetch_deals(merchant_name)
