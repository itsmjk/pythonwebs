import requests
import time

def send_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # This allows HTML formatting in the message
    }
    response = requests.post(url, data=data)
    return response.json()

# Replace with your bot token and chat ID
bot_token = "7253586168:AAFXyf3i6-QPHNE5nJZ_-Uh-_DmpliN6HXM"
chat_id = -1001895503131

# Messages
message_1 = 'Welcome to Houston, Texas Cannabis Marketplace! Click <a href="https://t.me/+xb0oBA1HfSBiZjYx">here</a> to join Passion Farms Wholesale catalog.'
message_2 = 'Hello, Welcome to the Houston Market hosted by Passion Farms. Make sure you check the rules before sending any messages.'

# Timer setup
one_hour = 3600  # 1 hour in seconds
four_hours = 4 * 3600  # 4 hours in seconds
time_since_last_message_2 = 0

while True:
    # Send message 1 every hour
    response = send_message(bot_token, chat_id, message_1)
    print('Message 1 posted, now sleeping for 1 hour.')

    # Sleep for 1 hour
    time.sleep(one_hour)
    
    # Update time since last message 2 was sent
    time_since_last_message_2 += one_hour

    # Send message 2 every 4 hours
    if time_since_last_message_2 >= four_hours:
        response = send_message(bot_token, chat_id, message_2)
        print('Message 2 posted, resetting 4-hour timer.')
        time_since_last_message_2 = 0
