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
chat_id = -1002407772862


message = 'Hello, Welcome to the Houston Market hosted by Passion Farms. Make sure you check the rules before sending any messages, and click the <a href="https://t.me/+hKOUOzlePMJlYzY5">link</a> below to check out our wholesale catalogue. https://t.me/+hKOUOzlePMJlYzY5'

# Timer setup
four_hours = 4 * 3600  # 4 hours in seconds

# Send the first message immediately when the code starts
response = send_message(bot_token, chat_id, message)
print('Message posted, now sleeping for 4 hours.')

while True:
    # Sleep for 4 hours
    time.sleep(four_hours)
    
    # Send the message every 4 hours
    response = send_message(bot_token, chat_id, message)
    print('Message posted, now sleeping for 4 hours.')
