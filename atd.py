from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
import re

# Your Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'

# Initialize the Telegram client
client = TelegramClient('sessoinx1s', api_id, api_hash)

# Function to delete messages with keywords
def delete_messages_with_keywords_and_links(channel_entity, keywords, except_member_username):
    try:
        messages = client.get_messages(channel_entity, limit=3)
        for message in messages:
            print(message.sender.username)
            # Check if the message contains any of the keywords
            if any(re.search(r'\b{}\b'.format(re.escape(keyword)), message.text, re.IGNORECASE) for keyword in keywords):
                print("Message to delete:", message.text)
                try:
                    client.delete_messages(channel_entity, [message.id])
                    print("Message deleted successfully!")
                    continue
                except ChatAdminRequiredError:
                    print("You don't have the necessary permissions to delete messages.")
                except Exception as e:
                    print(f"Error deleting message: {e}")
            # Check if the message contains any links
            if 'http' in message.text:
                # Check if the message sender's username is the except_member_username
                if message.sender.username == except_member_username:
                    print("Message contains link but is sent by the except member.")
                    continue  # Skip messages sent by the except member
                else:
                    print("Message contains a link:", message.text)
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
        except_member_username = 'harnoli7'  # Specify the username of the member whose messages should be excluded
        keywords = ['black rock', 'candy', 'chemical', 'cookies', 'dice', 'gravel', 'grit', 'hail', 'hard rock',
                    'jelly beans', 'purple caps', 'rocks', 'scrabble', 'sleet', 'snow coke', 'tornado', 'blow',
                    'bump', 'c', 'big c', 'coke', 'crack', 'dust', 'flake', 'line', 'nose candy', 'pearl', 'rail',
                    'snow', 'sneeze', 'sniff', 'speedball', 'toot', 'white rock', 'sizzurp', 'drank', 'barre',
                    'purple jelly', 'wok', 'texas tea', 'memphis mud', 'dirty sprite', 'tsikuni', 'purple triss',
                    'speed', 'crank', 'ice', 'chalk', 'wash', 'trash', 'dunk', 'gak', 'pookie', 'christina', 'no doze',
                    'white cross', 'cotton candy', 'rocket fuel', 'scooby snax', 'cocain', 'cocaine', 'meth', 'heroin', 'eight ball', ' XANAX',
                    'fentanyls', 'fentanyl', 'addys']
        while True:
            delete_messages_with_keywords_and_links(channel_entity, keywords, except_member_username)
    finally:
        client.disconnect()
if __name__ == "__main__":
    main()
