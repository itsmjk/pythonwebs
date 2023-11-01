from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from telethon import TelegramClient, sync
from datetime import datetime, timedelta, timezone
import requests
import re
from telethon.tl.types import MessageEntityUrl
import pandas as pd
import schedule
import time
import pytz
import sys

# Replace these variables with your own values
page_access_token = 'EAAJaYuHW2EYBO57DziD4T5t5kJhoACZAsg6s6UfKM24XBaeokee0iLdDy6l9np0nXrZAtg7gpXU6gGMdZBokRneNJpZAwkzoElvP1EBUZAbWBIphAU7xxmaHr27k350a7ZBLHZBduidxZBbvKbJjn71WrIZBe5ZBf1g24oOJqZBfr2cACWdXKw8PR6fzZCTBDWP2ICpv'
page_access_token_our = 'EAAU1c5aXSKMBOZCGq0BwX5W0aFt7I2WvZCGcOypUdXexd05OJ1oAAwHtxFmfSMNlkZBsq8lJBIufY74FP5vamDApZCGRUZB20gIsoxxNOPOGVy9VeqNUAydGaFsaPDF86MzNosrnuZA1dtOu89irT9GLZBxw9RyvC40wdZB7RzEFxBC7ZBZA14P1Xc5r0UknkSkZC6o'
page_id = '101450682659753'
page_id_our = '126329840572666'
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
channel_usernames = ['hcstealdealsUS', 'USA_Deals_and_Coupons', 'deals_shopping_usa']  # Add more channel usernames as needed
session_name = 'sessoinx7j'
mychannel = 'ktest1u38'
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
        # Get the messages from the group sent within the last 60 minutes
        time_60_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=200)
        
        # Get messages from the channel within the last 60 minutes
        entity = client.get_entity('ktest1u38')
        last_channel_messages = []
        messages = client.get_messages(entity, limit=70)
        for message in messages:
            if message.date.replace(tzinfo=timezone.utc) < time_60_minutes_ago:
                break
            last_channel_messages.append(message)

        # Combine last messages from the group and channel
        all_last_messages = last_channel_messages

        # Extract the link from the ad_data
        link_start = ad_data.find("https://")
        link_end = ad_data.find("\n", link_start)
        if link_end == -1:
            link = ad_data[link_start:]
        else:
            link = ad_data[link_start:link_end]
        print(link)
        # Extract the part of the link that starts with '/' and ends with '?'
        link_parts = link.split('/')
        filtered_parts = [part for part in link_parts if '?' in part]
        if filtered_parts:
            link = filtered_parts[0]
        else:
            link = ""  # If no valid link found, set it to empty
        # Check if the link exists in the last messages within the last 60 minutes
        message_exists = any(link in message.text for message in all_last_messages if message.text)
        if not message_exists:
            # If the message is not already present, send it
            client.send_message(mychannel, ad_data)
            print("Message sent to the Channel.")
        else:
            print("Message already exists in the last messages of the group and channel within the last 60 minutes. Skipping.")

    except Exception as e:
        print("Error occurred while sending message to group:", e)

# Function to modify links in the deal message
def modify_links_in_deal(deal):
    # Define a regular expression pattern to match URLs, including amzn.to
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|amzn\.to/[a-zA-Z0-9]+)'
    
    # Find all URLs in the deal text
    urls = re.findall(url_pattern, deal)
    
    # Replace each URL with the modified version
    for url in urls:
        # Expand the short link
        expanded_link = expand_short_link(url)
        print(expanded_link)
        # Modify the link as needed
        modified_link = expanded_link + "?linkCode=ml1&tag=bigdeal09a-20"
        modified_link_our = expanded_link + "?linkCode=ml1&tag=usadeals27-20"
        # Replace the original URL with the modified one in the deal text
        deal = deal.replace(url, modified_link)
        deal_our = deal.replace(modified_link, modified_link_our)
        # new_text = "STAY ACTIVE - Like this post when you see it 👍 \n"
        # deal = new_text + deal
        link = expanded_link
        dealcheck = is_link_already_posted(link)
        if dealcheck:
            # return deal
            return deal, modified_link, deal_our, modified_link_our
        else:
            return False

def is_link_already_posted(link):
    try:
        # Define the Facebook API endpoint URL for the page's feed
        fb_api_url = f'https://graph.facebook.com/v13.0/{page_id}/feed'

        # Parameters for the API request
        params = {
            'access_token': page_access_token,
            'limit': 100  # Limit to the last 5 posts
        }
        # Send a GET request to the API
        deals_already_in_page = []
        response = requests.get(fb_api_url, params=params)
        if response.status_code == 200:
            posts_data = response.json().get('data', [])
            current_time = datetime.now(timezone.utc)

            # Iterate through the last 5 posts
            for post in posts_data:
                created_time = post.get('created_time', None)
                if created_time:
                    try:
                        post_time = date_parser.parse(created_time)
                    except Exception as date_parse_error:
                        print(f"Error parsing 'created_time': {date_parse_error}")
                        continue  # Skip this post and continue with the next one

                    # Check if the post was made within the last 5 hours
                    if (current_time - post_time) > timedelta(hours=24):
                        break
                    deals_already_in_page.append(post)
            message_exists = any(link in post['message'] for post in deals_already_in_page)
            if not message_exists:
                return True
            else:
                return False

        else:
            print(f"Response is not 200: {response.text}")

    except Exception as e:
        print(f"Error checking if link is already posted: {e}")

    return False

# Function to expand short links
def expand_short_link(short_link):
    try:
        if short_link.startswith("amzn.to"):
            short_link = "https://" + short_link  # Prepend http:// to amzn.to links
        response = requests.head(short_link, allow_redirects=True)
        expanded_link = response.url

        # Find the index of the first occurrence of 8 or more consecutive capital letters or digits
        match = re.search(r'[A-Z0-9]{8,}', expanded_link)
        if match:
            start_index = match.start()
        else:
            start_index = 0

        # Find the index of the first "?" character after the start_index
        question_mark_index = expanded_link[start_index:].find("?")
        
        # Find the index of the first "/" character after the start_index
        slash_index = expanded_link[start_index:].find("/")

        if question_mark_index != -1 and slash_index != -1:
            # Determine the position of the first occurrence of "?" or "/"
            position = min(question_mark_index, slash_index) + start_index
        elif question_mark_index != -1:
            position = question_mark_index + start_index
        elif slash_index != -1:
            position = slash_index + start_index
        else:
            position = len(expanded_link)

        modified_link = expanded_link[:position]

        return modified_link
    except Exception as e:
        print(f"Error expanding short link: {e}")
        return short_link

# Calculate the date 24 hours ago from now in UTC timezone
time_duration_minutes = 40
# Function to scrape messages from a channel and print links
def scrape_channel_messages(channel_username):
    try:
        # Get the entity of the channel
        entity = client.get_entity(channel_username)

        time_since = datetime.now(timezone.utc) - timedelta(minutes=time_duration_minutes)

        # Get a larger number of messages from the channel (e.g., 1000)
        messages = client.get_messages(entity, limit=90)

        for message in messages:
            if message.message:
                if message.date.replace(tzinfo=timezone.utc) >= time_since:
                    message_text = message.message
                    deal = ''
                    if channel_username == 'hcstealdealsUS':
                        # Check if the message text contains a number followed by '%'
                        match = re.search(r'(\d+)% off', message_text)
                        if match:
                            matched_text = match.group(0)  # Get the matched text
                            percentage = int(matched_text.split('%')[0])  # Extract the percentage value as an integer
                            if percentage >= 29:  # Check if the percentage is 30% or more
                                deal += f"About {matched_text} 🔥\n"
                            else:
                                continue
                        else:
                            continue
                        if "coupon" in message.message.lower():
                            deal += "Apply Coupon\n"

                    elif channel_username == 'USA_Deals_and_Coupons':
                        # Check if the message contains price information
                        price_matches = re.findall(r'(\d+\.\d{2})\$', message_text)
                        if len(price_matches) == 2:
                            price1 = float(price_matches[0])
                            price2 = float(price_matches[1])
                            price_difference = price2 - price1
                            percentage_reduction = int((price_difference / price2) * 100)
                            if percentage_reduction >= 29:  # Check if the percentage is 30% or more
                                deal += f"About {percentage_reduction}% off 🔥\n"
                            else:
                                continue
                        else:
                            continue
                        if "coupon" in message.message.lower():
                            deal += "Apply Coupon\n"
                            
                    elif channel_username == 'deals_shopping_usa':
                        # Check if the message text contains a number followed by '%'
                        match = re.search(r'(\d+)%', message_text)
                        if match:
                            matched_text = match.group(0)  # Get the matched text
                            percentage = int(matched_text.split('%')[0])  # Extract the percentage value as an integer
                            if percentage >= 29:  # Check if the percentage is 30% or more
                                deal += f"About {matched_text} 🔥\n"
                            else:
                                continue
                        else:
                            continue
                        if "coupon" in message.message.lower():
                            deal += "Apply Coupon\n"

                    # Check if the message contains a link
                    match = re.search(r'https?://\S+', message_text)
                    if match:
                        found_link = match.group()
                        final_url = resolve_short_link(found_link)
                        if "/?" in final_url:
                            final_url = final_url.replace("/?", "?")
                        if final_url:
                            # Find the index of "?" in the final URL
                            question_mark_index = final_url.find("?")
                            if question_mark_index != -1:
                                final_url = final_url[:question_mark_index]
                            # Add the "?tag=dealsbargains00-21" to the final URL
                            final_url = final_url + "?linkCode=ml1&tag=Bigdeal09a-20"
                            deal +=  final_url + "\n"
                            ad_data = deal
                            ad_data += "#ad\n"
                            new_text = "STAY ACTIVE -Like this post when you see it 👍 \n"
                            ad_data = new_text + ad_data
                            # send_to_group(ad_data)
                            deal = ad_data
                            result = modify_links_in_deal(deal)
                            if result is not None and result is not False:
                                deal, modified_link, deal_our, modified_link_our = result
                                try:
                                    if '%' in deal:
                                        # send_to_facebook_group(modified_deal)
                                        # client(SendMessageRequest(-928459610, message=modified_deal))
                                        fb_api_url = f'https://graph.facebook.com/v13.0/{page_id}/feed'
                                        fb_params = {
                                            'access_token': page_access_token,
                                            'message': deal,
                                            'link': modified_link
                                        }
                                        fb_response = requests.post(fb_api_url, data=fb_params)
                                        if fb_response.status_code == 200:
                                            print("Message posted on your page.")
                                            # time.sleep(360)
                                        else:
                                            print("Error posting message on your page:", fb_response.text)

                                        #post to group
                                        group_id = 375273304559842
                                        fb_group_api_url = f'https://graph.facebook.com/v13.0/{group_id}/feed'
                                        fb_group_params = {
                                            'access_token': page_access_token,
                                            'message': deal,
                                            'link': modified_link
                                        }
                                        fb_group_response = requests.post(fb_group_api_url, data=fb_group_params)
                                        if fb_group_response.status_code == 200:
                                            print(f"Message posted on the Facebook group. Now wait 360 seconds")
                                            time.sleep(360)
                                        else:
                                            print(f"Error posting message on the Facebook group (ID: {group_id}):", fb_group_response.text)
                                        
                                        # #post to Our page
                                        # fb_api_url = f'https://graph.facebook.com/v13.0/{page_id_our}/feed'
                                        # fb_params = {
                                        #     'access_token': page_access_token_our,
                                        #     'message': deal_our,
                                        #     'link': modified_link_our
                                        # }
                                        # fb_response = requests.post(fb_api_url, data=fb_params)
                                        # if fb_response.status_code == 200:
                                        #     print("Message posted on OUR page.")
                                        #     # time.sleep(360)
                                        # else:
                                        #     print("Error posting message on OUR page:", fb_response.text)

                                        # #post to our group
                                        # group_id_our = 712288753692244
                                        # fb_group_api_url = f'https://graph.facebook.com/v13.0/{group_id_our}/feed'
                                        # fb_group_params = {
                                        #     'access_token': page_access_token_our,
                                        #     'message': deal_our,
                                        #     'link': modified_link_our
                                        # }
                                        # fb_group_response = requests.post(fb_group_api_url, data=fb_group_params)
                                        # if fb_group_response.status_code == 200:
                                        #     print(f"Message posted on OUR Facebook group. Now wait 360 seconds")
                                        #     time.sleep(360)
                                        # else:
                                        #     print(f"Error posting message on OUR Facebook group (ID: {group_id_our}):", fb_group_response.text)
                                except Exception as e:
                                    print(f"Error sending deal: {e}")
                        else:
                            print("Deal returned FALSE, probably exists")

                    else:
                        continue

    except Exception as e:
        print(f"Error occurred while scraping {channel_username}: {e}")
        return []

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
    # uk_start_time = current_uk_time.replace(hour=2, minute=30, second=0, microsecond=0)
    # uk_end_time = current_uk_time.replace(hour=3, minute=55, second=0, microsecond=0)

    # if uk_start_time <= current_uk_time <= uk_end_time:
    #     print("Current time is within the specified time range. Stopping the program.")
    #     # sys.exit()  # Exit the program gracefully
    #     time.sleep(36000)

# Schedule the task to run every 5 seconds
schedule.every(7).minutes.do(scheduled_task)

# Run the scheduled task
while True:
    schedule.run_pending()
    time.sleep(5)
