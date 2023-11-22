from selenium import webdriver
from bs4 import BeautifulSoup
from telethon import TelegramClient, sync
from telethon.tl.types import MessageEntityUrl
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import schedule
import json
import time
import re

api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sessoinx1hu'
telegram_group_id = -4091450544  # Replace with the group ID where you want to send the messages
# ourtelgroup_id = -1001500844459
mychannel = 'xchannnal'
client = TelegramClient(session_name, api_id, api_hash)
client.start()

def send_to_group(ad_data, image_url):
    try:
        # Get the messages from the group sent within the last 60 minutes
        time_60_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=200)
        last_group_messages = []
        group_messages = client.get_messages(telegram_group_id, limit=90)
        for message in group_messages:
            if message.date.replace(tzinfo=timezone.utc) < time_60_minutes_ago:
                break
            if message.text is not None:
                last_group_messages.append(message)

        # # Get messages from the channel within the last 60 minutes
        # entity = client.get_entity('xchannnal')
        # last_channel_messages = []
        # messages = client.get_messages(entity, limit=90)
        # for message in messages:
        #     if message.date.replace(tzinfo=timezone.utc) < time_60_minutes_ago:
        #         break
        #     last_channel_messages.append(message)

        # Extract the link from the ad_data
        link_start = ad_data.find("https://")
        link_end = ad_data.find("\n", link_start)
        if link_end == -1:
            link = ad_data[link_start:]
        else:
            link = ad_data[link_start:link_end]

        # Extract the part of the link that starts with '/' and ends with '?'
        link_parts = link.split('/')
        filtered_parts = [part for part in link_parts if '?' in part]
        if filtered_parts:
            link = filtered_parts[0]
        else:
            link = ""  # If no valid link found, set it to empty
        
        # Check if the link exists in the last messages within the last 60 minutes
        message_exists = any(link in message.text for message in last_group_messages)
        # Replace "hugebargains-21" with "ukdeals27-21"
        # for_channel = ad_data
        # for_our_group = ad_data.replace("hugebargains-21", "ukdeals27-21")
        
        if not message_exists:
            # If the message is not already present, send it
            # client.send_message(telegram_group_id, ad_data)
            client.send_file(telegram_group_id, image_url, caption=ad_data)
            print("Message sent to the group.")
            # client.send_message(mychannel, for_channel)
            # print("Message sent to the Channel.")
            # client.send_message(ourtelgroup_id, for_our_group)
            # print("Message sent to our group.")
        else:
            print("Message already exists in the last messages of the group and channel within the last 60 minutes. Skipping.")
    except Exception as e:
        print("Error occurred while sending message to group:", e)

# Function to fetch deals based on a merchant name and posted time
def fetch_deals(merchant_name="", max_hours=4):
    # Start a headless Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # The URL of the web page
    url = "https://www.hotukdeals.com/search/deals?merchant-id=1650"
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
        time_element = article.find("span", class_="metaRibbon lbox--v-1 boxAlign-ai--all-c overflow--wrap-off space--l-3 text--color-greyShade")
        time_elementx = article.find("span", class_="hide--toW2 metaRibbon lbox--v-1 boxAlign-ai--all-c overflow--wrap-off space--l-3 text--color-greyShade")
        if time_elementx:
            time_element = time_elementx
        
        if temp_element and time_element:
            temp_text = temp_element.text.strip()
            posted_time_text = time_element.find("span").text.strip()

            if temp_text.endswith("°") and int(temp_text[:-1]) > 1:
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
                            time_match = re.search(r"(\d+\s*h, )?(\d+) m ago", posted_time_text)
                            if time_match:
                                posted_hours_ago = int(time_match.group(1).strip(' h, ')) if time_match.group(1) else 0
                                posted_minutes_ago = int(time_match.group(2))
                                total_posted_minutes_ago = posted_hours_ago * 60 + posted_minutes_ago

                                if total_posted_minutes_ago <= (max_hours * 60):
                                    deal_url = f"https://www.hotukdeals.com/visit/homeyou/{code}"

                                    # Send an additional GET request to the URL to follow redirection
                                    response = requests.get(deal_url, timeout=10)  # Add a timeout of 10 seconds
                                    print(response)
                                    ad_data = ""
                                    if response.status_code == 503:
                                        # Use the URL after redirection
                                        final_url = response.url
                                        # Find the index of the first occurrence of 8 or more consecutive capital letters or digits
                                        match = re.search(r'[A-Z0-9]{8,}', final_url)
                                        if match:
                                            start_index = match.start()
                                        else:
                                            start_index = 0

                                        # Find the index of the first "?" character after the start_index
                                        question_mark_index = final_url[start_index:].find("?")
                                        
                                        # Find the index of the first "/" character after the start_index
                                        slash_index = final_url[start_index:].find("/")

                                        if question_mark_index != -1 and slash_index != -1:
                                            # Determine the position of the first occurrence of "?" or "/"
                                            position = min(question_mark_index, slash_index) + start_index
                                        elif question_mark_index != -1:
                                            position = question_mark_index + start_index
                                        elif slash_index != -1:
                                            position = slash_index + start_index
                                        else:
                                            position = len(final_url)

                                        final_url = final_url[:position]
                                        final_url = final_url + "?linkCode=ml1&tag=hugebargains-21"
                                        # question_mark_index = final_url.find("?")

                                        # if question_mark_index != -1:  # If "?" is found in the URL
                                        #     # Replace the text after "?" with "ref=abc"
                                        #     modified_url = final_url[:question_mark_index + 1] + "ref=abc"
                                        #     final_url = modified_url
                                        # print(f"7-digit code: {code}")
                                        # print(f"Title: {title}")
                                        # print(f"Price: {price}")
                                        # print(f"URL: {final_url}")
                                        # print(f"Temperature: {temp_text}")
                                        # print(f"Posted: {posted_time_text}")
                                        ad_data += f"About {price} 🔥\n"
                                        voucher = re.search(fr'{re.escape("voucher")}', title, flags=re.IGNORECASE)
                                        if voucher:
                                            ad_data += f"Apply Voucher 💛\n"
                                        subscribe = re.search(r'\b(subscribe|s\s*&\s*s)\b', title, flags=re.IGNORECASE)
                                        if subscribe:
                                            ad_data += f"Cheaper with S&S \n"
                                        
                                        ad_data += f"{final_url}\n"
                                        ad_data += "#ad\n"
                                        # print(ad_data)
                                        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")

                                        driver = webdriver.Chrome(options=options)
                                        wait = WebDriverWait(driver, 10)

                                        url = "https://www.amazon.co.uk/dp/B0B9SN1QYC?linkCode=ml1&tag=xxxxx-21"
                                        driver.get(final_url)
                                        try:
                                            # Dismiss the cookies popup if it exists
                                            cookies_popup = wait.until(EC.presence_of_element_located((By.ID, "sp-cc-accept")))
                                            cookies_popup.click()
                                        except Exception as e:
                                            print(f"Could not dismiss the cookies popup: {e}")

                                        # Change the zoom level if needed
                                        driver.execute_script("document.body.style.zoom='80%'")

                                        # Fetch the product image URL
                                        try:
                                            product_image = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
                                            image_url = product_image.get_attribute("src")
                                            # client.send_file(mychannel, image_url, caption=ad_data)
                                            print(f"Product Image URL: {image_url}")
                                            send_to_group(ad_data, image_url)
                                        except Exception as e:
                                            print(f"Could not fetch the product image: {e}")
                                        # print(ad_data)
                                        
                                        print('sent')
                                    elif response.status_code == 200:
                                        # Use the URL after redirection
                                        final_url = response.url
                                        print(f"7-digit code: {code}")
                                        print(f"Title: {title}")
                                        print(f"Price: {price}")
                                        print(f"URL: {final_url}")
                                        print(f"Temperature: {temp_text}")
                                        print(f"Posted: {posted_time_text}")
                                        print()
                                    else:
                                        print(f"Failed to fetch the deal URL: {deal_url}")
                                    
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                        continue  # Continue to the next deal

# Input your desired merchant name or leave it empty to fetch all deals
# Example: merchant_name = "Amazon" or merchant_name = ""
def run_code():
    merchant_name = ""
    max_hours = 4
    fetch_deals(merchant_name, max_hours)

# Schedule the job to run every 10 minutes
schedule.every(30).minutes.do(run_code)

while True:
    schedule.run_pending()
    time.sleep(5)
