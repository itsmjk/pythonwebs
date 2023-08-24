from telethon import TelegramClient, sync
from datetime import datetime, timedelta, timezone
import requests
import re
from telethon.tl.types import MessageEntityUrl
import pandas as pd
import schedule
import time

# Replace these variables with your own values
api_id = 26982527
api_hash = '468f15380793dd40b9071e2379d08559'
channel_usernames = ['KTsDealsAndDiscounts', 'thriftydealsuk', 'rockingdealsuk']  # Add more channel usernames as needed
session_name = 'mysession'
telegram_group_id = -1001951330090  # Replace with the group ID where you want to send the messages

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
        # Get the last 10 messages from the group
        last_messages = client.get_messages(telegram_group_id, limit=10)

        # Extract the link from the ad_data
        link_start = ad_data.find("https://")
        link_end = ad_data.find("\n", link_start)
        if link_end == -1:
            link = ad_data[link_start:]
        else:
            link = ad_data[link_start:link_end]
        
        # Check if the link exists in the last_messages
        message_exists = any(link in message.text for message in last_messages)
        
        if not message_exists:
            # If the message is not already present, send it
            client.send_message(telegram_group_id, ad_data)
            print("Message sent to the group.")
        else:
            print("Message already exists in the last 10 messages of the group. Skipping.")
    except Exception as e:
        print("Error occurred while sending message to group:", e)


# Function to scrape messages from a channel and print links
def scrape_channel_messages(channel_username):
    try:
        # Get the entity of the channel
        entity = client.get_entity(channel_username)

        # Calculate the date 24 hours ago from now in UTC timezone
        time_24_hours_ago = datetime.now(timezone.utc) - timedelta(hours=0.1)

        # Get a larger number of messages from the channel (e.g., 1000)
        messages = client.get_messages(entity, limit=1000)

        # List to store the data for each message
        message_data = []

        # Variables to keep track of the previous message and whether to print the previous message or not
        previous_message = None
        print_previous_message = False

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
                    if message.date.replace(tzinfo=timezone.utc) >= time_24_hours_ago:
                        ad_data = ""

                        # Use regular expression to find the price with "£" sign in the message
                        price_pattern = r'£(\d+(\.\d+)?)'
                        price_match = re.search(price_pattern, message_text)  # Use message_text instead of message.message
                        # Check if a match was found
                        if price_match:
                            # Get the price from the match object
                            price = price_match.group(1)
                            # Check if the message contains the word "subscribe" (case-insensitive)
                            if "subscribe" in message_text.lower():
                                ad_data += f"About £{price} via subscribe & save\n"
                            elif "promotion" in message_text.lower():
                                ad_data += f"About £{price} via on screen promotion\n"
                            else:
                                ad_data += f"About £{price}\n"
                            print("\n" + price)

                            # Check if the message contains the word "code" (case-insensitive)
                            if "code" in message_text.lower():
                                # Print the previous message if it exists and meets the condition to be printed
                                    if previous_message and print_previous_message:
                                        ad_data += "Code " + previous_message + "\n"
                            
                            # Check if the message contains the word "promo" (case-insensitive)
                            if "promo" in message_text.lower():
                                # Print the previous message if it exists and meets the condition to be printed
                                    if previous_message and print_previous_message:
                                        ad_data += "Code " + previous_message + "\n"

                            # Check if the message contains the word "voucher" (case-insensitive)
                            if "voucher" in message_text.lower():
                                ad_data += "Apply Voucher\n"

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
                                            final_url = final_url + "?tag=hugebargains-21"
                                            ad_data += "\n" + final_url + "\n"

                            if link_count > 1:
                                ad_data += "Add all\n"

                            ad_data += "#ad\n"

                            # Append the message data with the channel name to the list
                            message_data.append((channel_username, message.id, ad_data))
                            # Set the flag to print the previous message
                            print_previous_message = True

                            # Send the ad data to the specified Telegram group
                            send_to_group(ad_data)
                        else:
                            # Reset the flag if the current message does not contain the price
                            print_previous_message = False

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

# Schedule the task to run every 2 minutes
schedule.every(0.5).minutes.do(scheduled_task)

# Run the scheduled task
while True:
    schedule.run_pending()
    time.sleep(1)
