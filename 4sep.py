from telethon import TelegramClient, sync
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from telethon.tl.types import MessageEntityUrl
import pandas as pd
import schedule
import time
import pytz
import sys

# Replace these variables with your own values
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
channel_usernames = ['KTsDealsAndDiscounts', 'thriftydealsuk', 'rockingdealsuk']  # Add more channel usernames as needed
session_name = 'sessoinx3j'
mychannel = 'cryptoliontg'
telegram_group_id = -1001951330090  # Replace with the group ID where you want to send the messages
ourtelgroup_id = -1001500844459

# Connect to Telegram API
client = TelegramClient(session_name, api_id, api_hash)
client.start() 

# Function to resolve short links
def resolve_short_link(short_link):
    try:
        response = requests.get(short_link, allow_redirects=True)
        final_url = response.url
        return final_url
    except requests.exceptions.RequestException as e:
        print("Error occurred while resolving the link:", e)
        return None

# Function to send the ad data to the specified group
def send_to_group(ad_data):
    try:
        # Get the messages from the group sent within the last 60 minutes
        time_60_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=200)
        last_group_messages = []
        group_messages = client.get_messages(telegram_group_id, limit=80)
        for message in group_messages:
            if message.date.replace(tzinfo=timezone.utc) < time_60_minutes_ago:
                break
            if message.text is not None:
                last_group_messages.append(message)

        # Get messages from the channel within the last 60 minutes
        entity = client.get_entity('hugebargainsuk')
        last_channel_messages = []
        messages = client.get_messages(entity, limit=70)
        for message in messages:
            if message.date.replace(tzinfo=timezone.utc) < time_60_minutes_ago:
                break
            if message.text is not None:
                last_channel_messages.append(message)

        # Combine last messages from the group and channel
        all_last_messages = last_group_messages + last_channel_messages

        # Extract the link from the ad_data
        link_start = ad_data.find("https://")
        link_end = ad_data.find("\n", link_start)
        if link_end == -1:
            linkx = ad_data[link_start:]
        else:
            linkx = ad_data[link_start:link_end]

        # Extract the part of the link that starts with '/' and ends with '?'
        link_parts = linkx.split('/')
        filtered_parts = [part for part in link_parts if '?' in part]
        if filtered_parts:
            link = filtered_parts[0]
        else:
            link = ""  # If no valid link found, set it to empty
        
        # Check if the link exists in the last messages within the last 60 minutes
        message_exists = any(link in message.text for message in all_last_messages)
        # Replace "hugebargains-21" with "ukdeals27-21"
        for_channel = ad_data.replace("hugebargains-21", "ukdeals27-21")
        for_our_group = ad_data.replace("hugebargains-21", "ukdeals27-21")
        
        if not message_exists:
            # headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
            # }
            # response = requests.get(linkx, headers=headers)
            # if response.status_code == 200:
            #     soup = BeautifulSoup(response.content, 'html.parser')
                
            #     # Find the image element
            #     image_element = soup.find('img', {'id': 'landingImage'})  # Identifying the image by ID

            #     if image_element:
            #         image_url = image_element.get('src')
            #         print("Product Image URL:", image_url)
            #         ad_data += f"\n {image_url}"
            #         client.send_file(telegram_group_id, image_url, caption=ad_data)
            #         print("Message sent to the group.")
            #     else:
            #         print("Image not found on the page.")
            # If the message is not already present, send it
            client.send_message(telegram_group_id, ad_data)
            # client.send_file(telegram_group_id, image_url, caption=ad_data)
            print("Message sent to the group.")
            # time.sleep(7)
            # client.send_message(mychannel, for_channel)
            # print("Message sent to the Channel.")
            # client.send_message(ourtelgroup_id, for_our_group)
            # print("Message sent to our group.")
        else:
            print("Message already exists in the last messages of the group and channel within the last 60 minutes. Skipping.")
    except Exception as e:
        print("Error occurred while sending message to group:", e)

# Calculate the date 24 hours ago from now in UTC timezone
# time_duration_minutes = int(input("Enter the time duration in minutes: "))
time_duration_minutes = 5
# Function to scrape messages from a channel and print links
def scrape_channel_messages(channel_username):
    try:
        # Get the entity of the channel
        entity = client.get_entity(channel_username)

        time_since = datetime.now(timezone.utc) - timedelta(minutes=time_duration_minutes)

        # Get a larger number of messages from the channel (e.g., 1000)
        messages = client.get_messages(entity, limit=100)

        # List to store the data for each message
        message_data = []

        # Variables to keep track of the previous message and whether to print the previous message or not
        previous_message = None

        for message in messages:
            # Check if the message has content
            if message.message:
                # Check if the message contains the hyphen line "-------"
                if "-------" in message.message:
                    # Split the message by the hyphen line and take the part before it
                    message_text = message.message.split("-------")[0].strip()
                else:
                    message_text = message.message
                # Check if the message contains a link
                if message.entities and any(isinstance(entity, MessageEntityUrl) for entity in message.entities):
                    # Check if the message was sent within the last 24 hours
                    if message.date.replace(tzinfo=timezone.utc) >= time_since:
                        ad_data = ""
                        # price_pattern = r'(?:£(\d+(\.\d+)?)|(?<!\S)(\d+)p(?![^\s]))'
                        price_pattern = r'(?:£(\d+(,\d+)*(\.\d+)?)|(?<!\S)(\d+(,\d+)*\.\d*p)(?![^\s]))'
                        price_match = re.search(price_pattern, message_text)

                        if price_match:
                            if price_match.group(1):
                                price = price_match.group(1)
                                price = f"£{price}"
                            elif price_match.group(3):
                                price = price_match.group(3)
                                price = f"{price}p"

                            if "subscribe" in message_text.lower() or "subs and save" in message_text.lower():
                                ad_data += f"About {price} 🔥 via s&s\n"
                            elif "sub-n-sav" in message_text.lower():
                                    ad_data += f"About {price} 🔥 cheaper with s&s\n"
                            elif "promotion" in message_text.lower():
                                ad_data += f"About {price} 🔥 via on screen promotion\n"
                            elif "bogof" in message_text.lower():
                                ad_data += f"BOGOF Add 2 \n About {price} 🔥\n"
                            elif "lightning deal" in message_text.lower():
                                if "promo" in message_text.lower():
                                    ad_data += f"About {price} 🔥 via lightning deal & promo\n"
                                else:
                                    ad_data += f"About {price} 🔥 via lightning deal\n"
                            else:
                                ad_data += f"About {price} 🔥\n"
                            print("\n" + price)

                            # Check if the message contains the word "code" (case-insensitive)
                            if "code" in message_text.lower() or "promo" in message_text.lower():
                                # Print the previous message if it exists and meets the condition to be printed
                                    if previous_message and len(previous_message) < 11:
                                        ad_data += "Code " + previous_message + "\n"
                                    else:
                                        code_match = re.search(r'code[\s:_;\-\_]*([a-zA-Z\d]{8})', message_text.lower())
                                        if code_match:
                                            ad_data += "Code " + code_match.group(1).upper() + "\n"
                                            ky = "Code " + code_match.group(1).upper() + "\n"
                                        else:
                                            pass

                            # Check if the message contains the word "voucher" (case-insensitive)
                            if "voucher" in message_text.lower():
                                ad_data += "Apply Voucher 💛\n"

                            link_count = 0
                            for entity in message.entities:
                                if isinstance(entity, MessageEntityUrl):
                                    link = message_text[entity.offset:entity.offset + entity.length]  # Use message_text instead of message.message
                                    # Check if it's a short link and resolve it
                                    if link.startswith("http"):
                                        final_url = resolve_short_link(link)
                                        if final_url:
                                            link_count += 1
                                            # Find the index of "?" in the final URL
                                            question_mark_index = final_url.find("?")
                                            if question_mark_index != -1:
                                                final_url = final_url[:question_mark_index]
                                            # Add the "?tag=hugebargains-21" to the final URL
                                            final_url = final_url + "?linkCode=ml1&tag=hugebargains-21"
                                            ad_data += final_url + "\n"

                            if link_count > 1:
                                ad_data += "Add all\n"

                            ad_data += "#ad\n"
                            send_to_group(ad_data)
                            # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
                            # driver = webdriver.Chrome(options=options)
                            # wait = WebDriverWait(driver, 10)

                            # url = "https://www.amazon.co.uk/dp/B0B9SN1QYC?linkCode=ml1&tag=xxxxx-21"
                            # driver.get(final_url)
                            # # try:
                            # #     # Dismiss the cookies popup if it exists
                            # #     cookies_popup = wait.until(EC.presence_of_element_located((By.ID, "sp-cc-accept")))
                            # #     cookies_popup.click()
                            # # except Exception as e:
                            # #     print(f"Could not dismiss the cookies popup: {e}")

                            # # Change the zoom level if needed
                            # driver.execute_script("document.body.style.zoom='80%'")

                            # # Fetch the product image URL
                            # try:
                            #     product_image = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
                            #     image_url = product_image.get_attribute("src")
                            #     # client.send_file(mychannel, image_url, caption=ad_data)
                            #     print(f"Product Image URL: {image_url}")
                            #     message_data.append((channel_username, message.id, ad_data))
                            #     send_to_group(ad_data, image_url)
                                
                            # except Exception as e:
                            #     print(f"Could not fetch the product image: {e}")
                            # new_data = "**STAY ACTIVE - Like this post when you see it ✅️**"
                            # ad_data = new_data + "\n" + ad_data
                            # print(ad_data)

                            # Append the message data with the channel name to the list
                            # message_data.append((channel_username, message.id, ad_data))

                            # Send the ad data to the specified Telegram group
                            # send_to_group(ad_data)
                        else:
                            pass

                # Update the previous message with the current message
                previous_message = message_text

        return message_data

    except Exception as e:
        print(f"Error occurred while scraping {channel_username}: {e}")
        return []

# List to store all messages from different channels
# all_messages_data = []

# Function to schedule the task
def scheduled_task():
    # List to store all messages from different channels
    # all_messages_data = []

    # Run the scraping function for each channel
    for channel_username in channel_usernames:
        channel_messages_data = scrape_channel_messages(channel_username)
        # all_messages_data.extend(channel_messages_data)

    # Create a DataFrame to store the data
    # df = pd.DataFrame(all_messages_data, columns=["Channel Name", "Message ID", "Ad"])

    # Save the DataFrame to an Excel file
    # df.to_excel("output.xlsx", index=False)

    print("Scheduled task executed.")
    current_time = datetime.now(timezone.utc)

    # Define the UK time zone
    uk_timezone = pytz.timezone('Europe/London')

    # Convert current UTC time to UK time
    current_uk_time = current_time.astimezone(uk_timezone)

    # Create UK time objects for 2:00 AM and 2:10 AM
    # uk_start_time = current_uk_time.replace(hour=22, minute=00, second=0, microsecond=0)
    # uk_end_time = current_uk_time.replace(hour=22, minute=10, second=0, microsecond=0)

    # if uk_start_time <= current_uk_time <= uk_end_time:
    #     print("Current time is within the specified time range. Stopping the program.")
    #     # sys.exit()  # Exit the program gracefully
    #     time.sleep(30600)

# Schedule the task to run every 5 seconds
schedule.every(10).seconds.do(scheduled_task)

# Run the scheduled task
while True:
    schedule.run_pending()
    time.sleep(2)
