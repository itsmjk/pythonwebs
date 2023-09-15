from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
import re
import requests
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
import schedule
import time
import pytz
import sys

# Replace with your Telegram API credentials
# api_id = 24277666
# api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
# phone_number = 923016549616

# # Initialize the Telethon client
# client = TelegramClient('sessoinx1', api_id, api_hash)
# client.start(phone_number)

# Replace with your Page Access Token and Page ID
page_access_token = 'EAALlrgaLPWkBO9KZAQwNtiS2FYnfap8vZCx6yMN9PlOV7cRE3D4WFekx92rsk0ZCeVEO4TVpKUX9dwxsNT1pvznJ5NYhkUL4rdBLxpLSiSvyGawTtomqkqdGAZAbW9l6qTGsDgJ0QS9EvrjPq4oaFXGRUQicRDNdY7d2aUszeE2ny2voGYSd0aurPeUvUDd6'
page_id = '101450682659753'

# Define the API endpoint URLs
conversations_url = f'https://graph.facebook.com/v13.0/{page_id}/conversations'

# Parameters for the API requests
params = {
    'access_token': page_access_token,
    'limit': 2  # Number of conversations to retrieve
}

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
        # Replace the original URL with the modified one in the deal text
        deal = deal.replace(url, modified_link)
        deal += "\n #ad \n"
        link = expanded_link
        dealcheck = is_link_already_posted(link)
        if dealcheck:
            # return deal
            return deal, modified_link
        else:
            return False


def send_to_facebook_group(modified_deal):
    try:
        group_id = 375273304559842
        message = modified_deal
        fb_group_api_url = f'https://graph.facebook.com/v13.0/{group_id}/feed'
        fb_group_params = {
            'access_token': page_access_token,
            'message': message
        }
        fb_group_response = requests.post(fb_group_api_url, data=fb_group_params)
        if fb_group_response.status_code == 200:
            print(f"Message posted on the Facebook group (ID: {group_id}).")
        else:
            print(f"Error posting message on the Facebook group (ID: {group_id}):", fb_group_response.text)
    except Exception as e:
        print(f"Error sending deal to the Facebook group: {e}")

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
                # If the message is not already present, send it
                # print("Message sent to the PAGE.")
            else:
                return False
                # print("Message already exists withing timeframe. Skipping.")
                # Check if the given link is present in the post message
                # if link in post['message']:
                #     print('exists')
                # else:
                #     print('do not exist')
            # else:
            #     print('time doesnnot match')
            #     break

        else:
            print(f"Response is not 200: {response.text}")

    except Exception as e:
        print(f"Error checking if link is already posted: {e}")

    return False

def scrape_page_messages():
    print('Scraping has started....')
    # Step 1: Get the last 5 conversations
    conversations_response = requests.get(conversations_url, params=params)
    conversations_data = conversations_response.json()

    # Check if the request was successful
    if conversations_response.status_code == 200 and 'data' in conversations_data:
        for conversation in conversations_data['data']:
            conversation_id = conversation['id']
            
            # API endpoint for fetching messages in the conversation
            url = f'https://graph.facebook.com/v13.0/{conversation_id}?fields=messages.limit(1){{id,message}}&access_token={page_access_token}'

            # Send a GET request to the API
            response = requests.get(url)
            data = response.json()

            # Check if the response contains messages
            if 'messages' in data:
                messages = data['messages']['data']
                
                # Iterate through messages and print message IDs and text
                for message in reversed(messages):
                    message_id = message['id']
                    message_text = message.get('message', 'No text')
                    
                    # Split the message text into individual lines
                    lines = message_text.strip().split('\n')

                    # Initialize variables to store deals
                    current_deal = ""
                    deals = []

                    # Define a regular expression pattern to match lines that start with a number or a number followed by certain symbols
                    pattern = r'^\d+[\#\.;,:-]+.*|\d+$'

                    # Iterate through each line
                    for line in lines:
                        # Check if the line matches the pattern
                        if re.match(pattern, line.strip()):
                            # If the current deal has more than 3 lines, add it to the list of deals
                            if len(current_deal.split('\n')) > 3:
                                deals.append(current_deal.strip())
                            # Reset the current_deal variable
                            current_deal = ""
                        else:
                            # Check if the line contains the word "price"
                            # if 'price' not in line.lower() and 'discount' not in line.lower():
                            if 'price' not in line.lower() and ('discount' not in line.lower() or '$' not in line):
                                current_deal += line + '\n'

                    # Check if the last deal has more than 3 lines and add it to the list of deals
                    if len(current_deal.split('\n')) > 7:
                        deals.append(current_deal.strip())

                    # Iterate through each deal, modify links, and send them to your Telegram group
                    for deal in deals:
                        result = modify_links_in_deal(deal)
                        if result is not False:
                            deal, modified_link = result
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
                                    else:
                                        print("Error posting message on your page:", fb_response.text)
                            except Exception as e:
                                print(f"Error sending deal: {e}")
                        else:
                            print("Deal returned FALSE, probably exists")
                        # try:
                        #     if '%' in modified_deal:
                        #         # send_to_facebook_group(modified_deal)
                        #         client(SendMessageRequest(-928459610, message=modified_deal))
                        #         fb_api_url = f'https://graph.facebook.com/v13.0/{page_id}/feed'
                        #         fb_params = {
                        #             'access_token': page_access_token,
                        #             'message': modified_deal
                        #         }
                        #         fb_response = requests.post(fb_api_url, data=fb_params)
                        #         if fb_response.status_code == 200:
                        #             print("Message posted on your page.")
                        #         else:
                        #             print("Error posting message on your page:", fb_response.text)
                        # except Exception as e:
                        #     print(f"Error sending deal: {e}")

            else: 
                print("No messages found in the conversation.")
    else:
        print("Error retrieving conversations")

# Function to schedule the task
def scheduled_task():
        
    # Run the scraping function for each conversation
    scraping = scrape_page_messages()
    print("Scheduled task executed.")
    current_time = datetime.now(timezone.utc)

    # Define the UK time zone
    uk_timezone = pytz.timezone('Europe/London')

    # Convert current UTC time to UK time
    current_uk_time = current_time.astimezone(uk_timezone)

    # Create UK time objects for 2:00 AM and 2:10 AM
    uk_start_time = current_uk_time.replace(hour=2, minute=30, second=0, microsecond=0)
    uk_end_time = current_uk_time.replace(hour=2, minute=55, second=0, microsecond=0)

    if uk_start_time <= current_uk_time <= uk_end_time:
        print("Current time is within the specified time range. Stopping the program.")
        sys.exit()  # Exit the program gracefully

# Schedule the task to run every 20 minutes
schedule.every(10).minutes.do(scheduled_task)
print('code started')
# Run the scheduled task
while True:
    schedule.run_pending()
    time.sleep(5)
