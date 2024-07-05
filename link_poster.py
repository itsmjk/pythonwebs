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

# Replace with your bot token and the new chat id
bot_token = "7253586168:AAFXyf3i6-QPHNE5nJZ_-Uh-_DmpliN6HXM"
chat_id = -1001895503131
message = 'Welcome to Houston, Texas Cannabis Marketplace! Click <a href="https://t.me/+T7e74lLbT6ZmNWUx">here</a> to join Passion Farms Wholesale catalog.'

while True:
    response = send_message(bot_token, chat_id, message)
    print('link posted, now sleeping for 1 hour.')
    time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
