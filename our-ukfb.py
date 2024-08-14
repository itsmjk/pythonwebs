import re
import requests
from telethon.sync import TelegramClient, events

api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sessoinx1ouk'

# Replace with your Page Access Token and Page ID
page_access_token = 'EAAU1c5aXSKMBO5ODw3fbDbZBV1vuLxWYcMgA2TX32EFH1gdSLopMbwjLxrZAQlp6wTgeiUKOBHvVPIAZAwOko3yMuKFNRXBe0EYdcIyX5QPzHmZBdBupXxy31NXWfjbMapg4Mo35ih0go1dhXA9zMYvbDXNCU6mLVNIJGkoBjrjxfLBZBxrWjBhQZAZBmbEAA8K'
page_id = 131714140031420
group_id = 281598578025464

# Define a list of source channel usernames
source_channel_usernames = ['hugebargainsuk']  # Add your source channel usernames here

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)
print('Connected')

# Event handler for incoming messages in the source channels
@client.on(events.NewMessage(chats=source_channel_usernames))
async def handle_message(event):
    message_text = event.text
    print('okkk')

    # Define a regular expression pattern to match the link
    link_pattern = r'https://\S+'

    # Use re.sub to replace the link with an empty string
    new_message = re.sub(link_pattern, '', message_text)
    
    modified_link_message = message_text.replace('hugebargains-21', 'tk0f3-21')
    # Define a regular expression pattern to match URLs, including amzn.to
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|amzn\.to/[a-zA-Z0-9]+)'
    
    # Find all URLs in the deal text
    urls = re.findall(url_pattern, modified_link_message)
    
    # Replace each URL with the modified version
    for url in urls:
        # Expand the short link
        link = url
        #post to page
        fb_api_url = f'https://graph.facebook.com/v19.0/{page_id}/feed'
        fb_params = {
            'access_token': page_access_token,
            'message': new_message,
            'link': link
        }
        fb_response = requests.post(fb_api_url, data=fb_params)
        if fb_response.status_code == 200:
            print("Message posted on your page.")
            # time.sleep(360)
        else:
            print("Error posting message on your page:", fb_response.text)
        # #post to group
        # fb_group_api_url = f'https://graph.facebook.com/v13.0/{group_id}/feed'
        # fb_group_params = {
        #     'access_token': page_access_token,
        #     'message': new_message,
        #     'link': link
        # }
        # fb_group_response = requests.post(fb_group_api_url, data=fb_group_params)
        # if fb_group_response.status_code == 200:
        #     print('Message posted on FB group')
        # else:
        #     print(f"Error posting message on the Facebook group (ID: {group_id}):", fb_group_response.text)

# Start the client
with client:
    client.run_until_disconnected()
