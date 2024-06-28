import time
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
import re

# Your Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'

# Initialize the Telegram client
client = TelegramClient('sessoinx1s', api_id, api_hash)

# Function to delete messages with keywords
def delete_messages_with_keywords_and_links(channel_entity, keywords, except_member_usernames):
    try:
        messages = client.get_messages(channel_entity, limit=10)
        for message in messages:
            # Fetch the sender's username if available
            sender_username = message.sender.username if message.sender else None
            
            # Ensure the message has text content
            if not message.text:
                continue

            # Check if the message contains any links
            if 'http' in message.text:
                # Check if the message sender's username is in the except_member_usernames list
                if sender_username in except_member_usernames:
                    print("Message sent by an excluded member:", sender_username)
                    continue  # Skip messages sent by excluded members
                else:
                    print(sender_username)
                    print("Message contains a link:", message.text)
                    try:
                        client.delete_messages(channel_entity, [message.id])
                        print("Message deleted successfully!")
                    except ChatAdminRequiredError:
                        print("You don't have the necessary permissions to delete messages.")
                    except Exception as e:
                        print(f"Error deleting message: {e}")
                        
            # Check if the message contains any of the keywords
            if any(re.search(r'\b{}\b'.format(re.escape(keyword)), message.text, re.IGNORECASE) for keyword in keywords):
                print("Message to delete:", message.text)
                try:
                    if sender_username in except_member_usernames:
                        print("Message sent by an excluded member:", sender_username)
                        continue  # Skip messages sent by excluded members
                    else:
                        client.delete_messages(channel_entity, [message.id])
                        print("Message deleted successfully!")
                        continue
                        
                except ChatAdminRequiredError:
                    print("You don't have the necessary permissions to delete messages.")
                except Exception as e:
                    print(f"Error deleting message: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")

def main():
    try:
        client.start()
        
        # Replace 'https://t.me/+32GdcH9eAK0xODgx' with the invite link of your group
        invite_link = 'https://t.me/+32GdcH9eAK0xODgx'
        channel_entity = client.get_entity(invite_link)
        
        except_member_usernames = ['passionfarm', 'PassionFarms713', 'Zazziviz']  # List of usernames to be excluded
        keywords = ['black rock', 'candy', 'chemical', 'cookies', 'dice', 'gravel', 'grit', 'hail', 'hard rock',
                    'jelly beans', 'purple caps', 'rocks', 'scrabble', 'sleet', 'snow coke', 'tornado', 'blow',
                    'bump', 'c', 'big c', 'coke', 'crack', 'dust', 'flake', 'line', 'nose candy', 'pearl', 'rail',
                    'snow', 'sneeze', 'sniff', 'speedball', 'toot', 'white rock', 'sizzurp', 'drank', 'barre',
                    'purple jelly', 'wok', 'texas tea', 'memphis mud', 'dirty sprite', 'tsikuni', 'purple triss',
                    'speed', 'crank', 'ice', 'chalk', 'wash', 'trash', 'dunk', 'gak', 'pookie', 'christina', 'no doze',
                    'white cross', 'cotton candy', 'rocket fuel', 'scooby snax', 'cocain', 'cocaine', 'meth', 'heroin', 'eight ball', 'XANAX',
                    'fentanyls', 'fentanyl', 'addys']
        
        while True:
            delete_messages_with_keywords_and_links(channel_entity, keywords, except_member_usernames)
            print('Sleeping for a few seconds...')
            time.sleep(9)  # Sleep for 9 seconds before the next iteration
            
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
