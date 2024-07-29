import requests
import json
import time
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest

# Function to send message to Telegram group
def send_message_to_group(client, telegram_group_id, message):
    try:
        client(SendMessageRequest(
            peer=telegram_group_id,
            message=message,
            no_webpage=False
        ))
        print(f"Message sent: {message}")
        time.sleep(5)
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to fetch last messages from Telegram group
def get_last_group_messages(client, telegram_group_id, limit=80):
    try:
        time_60_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=90)
        last_group_messages = []
        group_messages = client.get_messages(telegram_group_id, limit=limit)
        
        for message in group_messages:
            if message.date > time_60_minutes_ago:
                last_group_messages.append(message.text)
        
        return last_group_messages
    except Exception as e:
        print(f"Error fetching group messages: {e}")
        return []

# List of keywords to check in the title
keywords = ['Polly pocket', 'Echo', 'Barbie', 'Wilkinson sword', 'Makita', 'Makeup Revolution', 'Provoke', 'Casio', 'Adidas', 'Lynx', 
            "L'Oreal", 'Eurohike', 'Honor', 'Ted Baker', 'Calvin Klein', 'Kit kat', 'GFW', 'Under Armour', 'Warrior supplements', 'Pepsi', 
            'Deer & Oak', 'Lego', 'Play-doh', 'E45', 'LOL surprise', 'Maybelline', 'G-Star', 'Elemis', 'Nicky soft', 'Columbia mens', 
            'William Morris', 'Remington', 'Desire Deluxe', 'Cerave', 'Gillette', 'Sharpie', 'Carex', 'Playmobil', 'Tower', 'TP-link', 
            'Sylvanian families', 'VTech', 'Fisher-price', 'KitchenCraft', 'Spear & Jackson', 'Baker Ross', 'Bosch', "Lily's kitchen", 
            'Old India', 'Melissa & Doug', 'Hot wheels', 'Grenade', 'Sanctuary spa', 'Castrol', 'Ravensburger', 'BRIO world', 'ORAL-B', 
            'Brushworks', 'Silentnight', 'PowerA', 'Paw patrol', 'Leapfrog', 'Asus', 'Max factor', "Wet 'n' wild", '7up', 'Rimmel', 'E.l.f.',
            'Nerf', 'Regina', 'Wella', 'Garnier', 'Sleepdown', 'Baylis & Harding', 'Joseph Joseph', 'Nike', 'Braun', 'Collection cosmetics', 
            'cmj rc cars', 'Faith in nature', 'Silentnight', 'Babyliss', 'Presto', 'Tommee tippee', 'Sally hansen']

api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'keepa_session'
telegram_group_id = -4008582023  # Replace with the group ID where you want to send the messages

client = TelegramClient(session_name, api_id, api_hash)
client.start()

while True:
    try:
        # Update client state to sync with the server
        client.get_me()

        url = 'https://api.keepa.com/deal?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&selection=%7B%22page%22%3A0%2C%22domainId%22%3A%222%22%2C%22excludeCategories%22%3A%5B1661657031%2C11961407031%2C229816%5D%2C%22includeCategories%22%3A%5B%5D%2C%22priceTypes%22%3A%5B0%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B10%2C2147483647%5D%2C%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C2147483647%5D%2C%22minRating%22%3A30%2C%22isLowest%22%3Atrue%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Atrue%2C%22filterErotic%22%3Atrue%2C%22singleVariation%22%3Atrue%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B2%2C3%2C4%2C5%5D%7D'

        response = requests.get(url)
        data = json.loads(response.text)

        if 'deals' in data and 'dr' in data['deals']:
            deals = data['deals']['dr']
            found_deals = []

            for deal in deals:
                title = deal['title']
                for keyword in keywords:
                    if keyword.lower() in title.lower():
                        asin = deal['asin']
                        found_deals.append(asin)
                        # print(f"ASIN: {asin}, Title: {title}")
                        break

            last_group_messages = get_last_group_messages(client, telegram_group_id)

            for asin in found_deals:
                asin_str = str(asin)
                if any(asin_str in message for message in last_group_messages):
                    print(f"ASIN {asin} found in group messages.")
                else:
                    print(f"ASIN {asin} not found in group messages.")

                    product_url = f'https://api.keepa.com/product?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&domain=2&stats=1&buybox=1&asin={asin}'
                    product_response = requests.get(product_url)
                    product_data = json.loads(product_response.text)

                    if 'products' in product_data and len(product_data['products']) > 0:
                        product = product_data['products'][0]
                        price = product['stats']['buyBoxPrice'] / 100.0
                        link = f"https://www.amazon.co.uk/dp/{asin}?linkCode=ml1&tag=biggerbargains-21"
                        message = f"About £{price:.2f} 🔥\n{link}\n#ad"
                        title = product.get('title', 'No title available')
                        message = f"{title} \n\n{message}"
                        print(message)
                        
                        send_message_to_group(client, telegram_group_id, message)
                    else:
                        print(f"No product details found for ASIN {asin}.")
        else:
            print("No deals found or error in response.")

    except Exception as e:
        print(f"Error: {e}")
    print('Waiting for 1000 seconds..!')
    time.sleep(1000)

client.disconnect()
