from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests
import urllib.parse
import datetime


TOKEN = '7473679669:AAH0XpYXBJOhPZxofmmEM1Yplx7saUDHwls'
FB_PAGE_ACCESS_TOKEN = 'EAAFZCfByZBm7wBOZBo5q4v53wF1YS8GHUdHy3ykhMbY5XNzPKjdNKTr4VFgMRelJ1T959LPHgqs09ciH8tq26ezwleTpZAt7EZBZBe3Do4pscG43IWykdY4Ifz3Wpb1ZBedh0l84r4ZA1Ddxhgrrh5rSuiY1p0CsohQhEKemnI8bdtjoIvTMyZBbjAFXZAZAeZC5fiRb'
FB_PAGE_ID = '470309979490090'  # Replace with your Facebook page ID

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is from a channel
    if update.channel_post:
        # Check if the message contains a link
        if 'http' in update.channel_post.text:
            # Separate the link from the message
            message_parts = update.channel_post.text.split('http')
            message = message_parts[0]
            link = 'http' + message_parts[1]
            # Send the message to the Facebook page
            send_to_facebook(message, link)

def send_to_facebook(message, link):
    # Encode the URL properly
    clean_link = link.split("\n")[0]  # Remove any newlines or unwanted characters
    # URL encode the clean link
    link = urllib.parse.quote(clean_link, safe=":/?&=")

    # Send the message to the Facebook page
    response = requests.post(f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/feed", params={'access_token': FB_PAGE_ACCESS_TOKEN, 'message': message, 'link': link})
    if response.status_code != 200:
        print(f"Failed to send message to Facebook: {response.status_code}, {response.text}")
    else:
        print('Message sent successfully.')
    print(f"Current Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Use filters for channel posts
    channel_post_filter = filters.TEXT & filters.ChatType.CHANNEL

    # Add the message handler for channel posts
    application.add_handler(MessageHandler(channel_post_filter, handle_message))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
