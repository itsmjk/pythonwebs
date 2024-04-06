import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import requests
import re
from telethon.sync import TelegramClient, events

# Define the scope of access and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('myjsonfile1.json', scope)
client = gspread.authorize(creds)

# Open the Google Spreadsheet by title and worksheet by title
spreadsheet = client.open("[ARCHIVE] FEBRUARY 24 Inventory")
worksheet = spreadsheet.worksheet("Current inventory list")

# Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sheet1'

# Initialize a Telethon client
client_telethon = TelegramClient(session_name, api_id, api_hash)

# Function to check for new rows and send them to Telegram
def check_for_new_rows_and_send():
    global initial_row_count
    current_rows = worksheet.get_all_values()
    current_row_count = len(current_rows)
    print(f"Last row number: {current_row_count}")
    
    if current_row_count > initial_row_count:
        new_rows_count = current_row_count - initial_row_count
        print(f"{new_rows_count} new row(s) inserted:")
        
        # Accumulate new rows for a single message
        rows_to_send = []
        for i in range(initial_row_count, current_row_count):
            row_data = current_rows[i]
            if row_data[0] and row_data[2] and row_data[4]:  # Check if A, C, and E columns are not empty
                rows_to_send.append((row_data, i + 1))

        # Send all accumulated rows to Telegram as one message
        if rows_to_send:
            send_rows_to_telegram(rows_to_send)

    # Update the initial_row_count
    for i in range(current_row_count - 1, 0, -1):
        row_data = current_rows[i]
        if row_data[0] and row_data[2] and row_data[4]:  # Check if A, C, and E columns are not empty
            initial_row_count = i + 1
            break

# Function to send multiple rows to Telegram as one message
def send_rows_to_telegram(rows_to_send):
    message = ""
    for row_data, row_number in rows_to_send:
        formatted_data = f"{row_data[4]} {row_data[0]} ({row_data[2]})"
        message += f"{formatted_data}\n"
    
    print(message)

    # Send the message to the Telegram channel
    try:
        client_telethon.send_message('harnoli7', message)
        print("Message sent to Telegram")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Get the initial number of rows
initial_row_count = len(worksheet.col_values(1))  # Set initial_row_count to the last filled row number

# Initial check for new rows, skipping empty rows
print("Initial check:")
check_for_new_rows_and_send()

# Start the Telethon client
with client_telethon:
    # Loop to continuously check for new rows every 10 seconds
    while True:
        print("Sleep time started.")
        time.sleep(70)
        print("Sleep time ended. Checking for new rows...")
        check_for_new_rows_and_send()
