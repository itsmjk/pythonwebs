import re
import requests
from telethon.sync import TelegramClient, events
from datetime import datetime, timedelta
import asyncio
from datetime import timezone
import google.generativeai as genai

# Configure the API key for Gemini
genai.configure(api_key='AIzaSyC66HQzns-fRh9YR_OviRVDqv4XI5t2JAo')

# Initialize a Gemini model appropriate for your use case
model = genai.GenerativeModel('models/gemini-1.5-flash')
# Keepa API key
API_KEY = '8fjl8kv6hd0q66k3lvbvnpmdtrjgld8dccd0deomgs4b9m5e1q4oghdmifb1v4qs'

api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sessionx7c'

# Define a list of source channel usernames
source_channel_usernames = ['USA_Deals_and_Coupons', 'xchannnal']  # Add your source channel usernames here

destination_channel_id = -1002460524303  # Replace with the destination channel's chat ID

# Create a TelegramClient instance
client = TelegramClient(session_name, api_id, api_hash)
print('Connected')



# Function to fetch product title using Keepa API
def fetch_title_from_keepa(asin):
    """Fetch the product title using the Keepa API."""
    try:
        response = requests.get(
            f"https://api.keepa.com/product?key={API_KEY}&domain=1&asin={asin}"
        )
        data = response.json()
        if "products" in data and data["products"]:
            return data["products"][0].get("title", "Product")
    except Exception as e:
        print(f"Error fetching title from Keepa: {e}")
    return "Product"

def generate_caption(title):
    directions_list_prompt = f"""
    Create a 5-6 word catchy caption for a product titled: {title} which should represent the title and these (🔥🔥) should be placed around the title.
    Don't add any extra tag to caption. Only return clean caption and caption should be in bold.
    """

    # Generate the response using the model
    response = model.generate_content([directions_list_prompt])
    
    # Return the generated content as a string
    return response.text

# Function to modify links in the deal message
def modify_links_in_deal(deal):
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|amzn\.to/[a-zA-Z0-9]+)'
    urls = re.findall(url_pattern, deal)
    for url in urls:
        expanded_link = expand_short_link(url)
        print(expanded_link)
        modified_link = expanded_link + "?linkCode=ml1&tag=muntarily-20"
        deal = deal.replace(url, modified_link)
        deal += "#ad \n"
        dealcheck = expanded_link
        if dealcheck:
            return deal, modified_link
        else:
            return False

# Function to expand short links
def expand_short_link(short_link):
    try:
        if short_link.startswith("amzn.to"):
            short_link = "https://" + short_link
        response = requests.head(short_link, allow_redirects=True)
        expanded_link = response.url

        match = re.search(r'[A-Z0-9]{8,}', expanded_link)
        start_index = match.start() if match else 0

        question_mark_index = expanded_link[start_index:].find("?")
        slash_index = expanded_link[start_index:].find("/")

        if question_mark_index != -1 and slash_index != -1:
            position = min(question_mark_index, slash_index) + start_index
        elif question_mark_index != -1:
            position = question_mark_index + start_index
        elif slash_index != -1:
            position = slash_index + start_index
        else:
            position = len(expanded_link)

        modified_link = expanded_link[:position]
        return modified_link, match.group() if match else None
    except Exception as e:
        print(f"Error expanding short link: {e}")
        return short_link, None

# Function to check for recent messages
async def has_recent_message(client, channel_id, minutes=1.5):
    try:
        async for message in client.iter_messages(channel_id, limit=5):
            if message.date and (datetime.now(timezone.utc) - message.date).total_seconds() < minutes * 60:
                return True
        return False
    except Exception as e:
        print(f"Error checking recent messages: {e}")
        return False

# Event handler for incoming messages in the source channels
@client.on(events.NewMessage(chats=source_channel_usernames))
async def handle_message(event):
    message_text = event.text
    message_media = event.media
    channel_username = event.chat.username

    try:
        destination_entity = await client.get_entity(destination_channel_id)
    except ValueError as e:
        print(f"Error fetching destination entity: {e}")
        return

    deal = ''

    # Custom logic for specific channels
    if channel_username == 'hcstealdealsUS':
        match = re.search(r'(\d+)% off', message_text)
        if match:
            matched_text = match.group(0)
            percentage = int(matched_text.split('%')[0])
            if percentage >= 29:
                deal += f"About {matched_text} 🔥\n"
            else:
                return
        else:
            return
        # if "coupon" in message_text.lower():
        #     deal += "Apply Coupon\n"

    if channel_username == 'USA_Deals_and_Coupons':
        price_matches = re.findall(r'(\d+\.\d{2})\$', message_text)
        if len(price_matches) == 2:
            price1 = float(price_matches[0])
            price2 = float(price_matches[1])
            price_difference = price2 - price1
            percentage_reduction = int((price_difference / price2) * 100)
            if percentage_reduction >= 2:
                deal += f"{percentage_reduction}% off 🔥\n"
            else:
                return
        else:
            return
        # if "coupon" in message_text.lower():
        #     deal += "Apply Coupon\n"

    if channel_username == 'xchannnal':
        print('xchannnal')
        price_matches = re.findall(r'(\d+\.\d{2})\$', message_text)
        if len(price_matches) == 2:
            price1 = float(price_matches[0])
            price2 = float(price_matches[1])
            price_difference = price2 - price1
            percentage_reduction = int((price_difference / price2) * 100)
            if percentage_reduction >= 25:
                deal += f"{percentage_reduction}% off 🔥\n"
            else:
                return
        else:
            return
        if "coupon" in message_text.lower():
            deal += "Apply Coupon\n"

    # Extract and process the link
    match = re.search(r'https?://(?!.*(?:whatsapp|media))\S+', message_text)
    if match:
        found_link = match.group()
        expanded_link, asin = expand_short_link(found_link)
        if not asin:
            print("ASIN not found in the link.")
            return

        title = fetch_title_from_keepa(asin)
        caption = generate_caption(title)

        deal += f"{caption}\n{expanded_link}?linkCode=ml1&tag=muntarily-20\n#ad\n"

    # Check for recent activity in the destination channel
    recent_message_found = await has_recent_message(client, destination_channel_id)
    if recent_message_found:
        print("Message skipped due to recent activity in the target channel.")
        return

    # Send the message to the destination channel
    if message_media:
        await client.send_message(destination_entity, deal, file=message_media)
        print('message sent')
    else:
        await client.send_message(destination_entity, deal)

# Start the client
with client:
    client.run_until_disconnected()
