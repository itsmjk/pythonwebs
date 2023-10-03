import re
import requests
from telethon.sync import TelegramClient, events

api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sessoinx7a'

# Define a list of source channel usernames
source_channel_usernames = ['hcstealdealsUS', 'USA_Deals_and_Coupons']  # Add your source channel usernames here

destination_channel_username = 'USAamazon_deals'  # Replace with the destination channel's username

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)
print('Connected')

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
        modified_link = expanded_link + "?linkCode=ml1&tag=kaysdealsusa-20"
        # Replace the original URL with the modified one in the deal text
        deal = deal.replace(url, modified_link)
        deal += "#ad \n"
        # new_text = "STAY ACTIVE - Like this post when you see it 👍 \n"
        # deal = new_text + deal
        dealcheck = expanded_link
        if dealcheck:
            # return deal
            return deal, modified_link
        else:
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

# Event handler for incoming messages in the source channels
@client.on(events.NewMessage(chats=source_channel_usernames))
async def handle_message(event):
    message_text = event.text
    message_media = event.media
    channel_username = event.chat.username

    # Initialize the destination entity (channel or chat)
    destination_entity = await client.get_entity(destination_channel_username)

    # Initialize the 'deal' variable
    deal = ''

    # Apply additional logic for the 'hcstealdealsUS' channel
    if channel_username == 'hcstealdealsUS':
        # Check if the message text contains a number followed by '%'
        match = re.search(r'(\d+)% off', message_text)
        if match:
            matched_text = match.group(0)  # Get the matched text
            percentage = int(matched_text.split('%')[0])  # Extract the percentage value as an integer
            if percentage >= 9:  # Check if the percentage is 30% or more
                deal += f"About {matched_text} 🔥\n"
            else:
                return  # Skip this message if the condition is not met
        else:
            return  # Skip this message if the condition is not met
        if "coupon" in message_text.lower():
            deal += "Apply Coupon\n"

    if channel_username == 'USA_Deals_and_Coupons':
        # Check if the message contains price information
        price_matches = re.findall(r'(\d+\.\d{2})\$', message_text)
        if len(price_matches) == 2:
            price1 = float(price_matches[0])
            price2 = float(price_matches[1])
            price_difference = price2 - price1
            percentage_reduction = int((price_difference / price2) * 100)
            if percentage_reduction >= 9:  # Check if the percentage is 30% or more
                deal += f"About {percentage_reduction}% off 🔥\n"
            else:
                return  # Skip this message if the condition is not met
        else:
            return  # Skip this message if the condition is not met
        if "coupon" in message_text.lower():
            deal += "Apply Coupon\n"

    if channel_username == 'harnoli7':
        print('harnoli')
        # Check if the message text contains a number followed by '%'
        match = re.search(r'(\d+)% off', message_text)
        if match:
            matched_text = match.group(0)  # Get the matched text
            percentage = int(matched_text.split('%')[0])  # Extract the percentage value as an integer
            if percentage >= 9:  # Check if the percentage is 30% or more
                deal += f"About {matched_text} 🔥\n"
            else:
                return  # Skip this message if the condition is not met
        else:
            return  # Skip this message if the condition is not met
        if "coupon" in message_text.lower():
            deal += "Apply Coupon\n"

    # Check if the message contains a link
    # Check if the message contains a link but not the word "whatsapp"
    match = re.search(r'https?://(?!.*whatsapp)\S+', message_text)
    if match:
    # match = re.search(r'https?://\S+', message_text)
    # if match:
        found_link = match.group()
        final_url = expand_short_link(found_link)
        if "/?" in final_url:
            final_url = final_url.replace("/?", "?")
        if final_url:
            # Find the index of "?" in the final URL
            question_mark_index = final_url.find("?")
            if question_mark_index != -1:
                final_url = final_url[:question_mark_index]
            # Add the "?linkCode=ml1&tag=bigdeal09a-20" to the final URL
            final_url = final_url + "?linkCode=ml1&tag=bigdeal09a-20"
            deal +=  final_url + "\n"
            ad_data = deal
            new_text = "STAY ACTIVE - Like this post when you see it 👍 \n"
            ad_data = new_text + ad_data
            # send_to_group(ad_data)
            deal = ad_data
            result = modify_links_in_deal(deal)
            if result is not None and result is not False:
                deal, modified_link = result
                try:
                    if '%' in deal:
                        print('done')
                    #         print(f"Error posting message on the Facebook group (ID: {group_id}):", fb_group_response.text)
                except Exception as e:
                    print(f"Error sending deal: {e}")
        else:
            print("Deal returned FALSE, probably exists")

    # Send the message to the destination channel without downloading media
    if message_media:
        await client.send_message(destination_entity, f"{deal}", file=message_media)
    else:
        await client.send_message(destination_entity, f"{deal}")

# Start the client
with client:
    client.run_until_disconnected()
