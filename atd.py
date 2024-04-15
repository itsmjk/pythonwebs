from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
import re

# Your Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'

# Initialize the Telegram client
client = TelegramClient('sessoinx1s', api_id, api_hash)

# Function to delete messages with keywords
def delete_messages_with_keywords(channel_entity, keywords):
    try:
        messages = client.get_messages(channel_entity, limit=10)
        for message in messages:
            if message.text is not None and any(re.search(r'\b{}\b'.format(re.escape(keyword)), message.text, re.IGNORECASE) for keyword in keywords):
                print("Message to delete:", message.text)
                try:
                    client.delete_messages(channel_entity, [message.id])
                    print("Message deleted successfully!")
                except ChatAdminRequiredError:
                    print("You don't have the necessary permissions to delete messages.")
                except Exception as e:
                    print(f"Error deleting message: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    try:
        client.start()
        # Replace 'YOUR_CHANNEL_USERNAME' with the username of your channel
        channel_username = 'testing_akjk'
        channel_entity = client.get_entity(channel_username)
        keywords = ['black rock', 'candy', 'chemical', 'cookies', 'dice', 'gravel', 'grit', 'hail', 'hard rock',
                    'jelly beans', 'purple caps', 'rocks', 'scrabble', 'sleet', 'snow coke', 'tornado', 'blow',
                    'bump', 'c', 'big c', 'coke', 'crack', 'dust', 'flake', 'line', 'nose candy', 'pearl', 'rail',
                    'snow', 'sneeze', 'sniff', 'speedball', 'toot', 'white rock', 'sizzurp', 'drank', 'barre',
                    'purple jelly', 'wok', 'texas tea', 'memphis mud', 'dirty sprite', 'tsikuni', 'purple triss',
                    'speed', 'crank', 'ice', 'chalk', 'wash', 'trash', 'dunk', 'gak', 'pookie', 'christina', 'no doze',
                    'white cross', 'cotton candy', 'rocket fuel', 'scooby snax', 'cocain', 'meth', 'heroin', 'eight ball']
        while True:
            delete_messages_with_keywords(channel_entity, keywords)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
