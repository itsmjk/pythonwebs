import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from telethon.sync import TelegramClient, events

# Define the scope of access and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('myjsonfile1.json', scope)
client = gspread.authorize(creds)

# Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sheet1'

# Initialize a Telethon client
client_telethon = TelegramClient(session_name, api_id, api_hash)

# Open the Google Spreadsheet by title and worksheet by title
spreadsheet = client.open("[ARCHIVE] FEBRUARY 24 Inventory")
worksheet = spreadsheet.worksheet("Current inventory list")

# Function to check for new rows and send them to Telegram
def check_for_new_rows_and_send(previous_rows):
    current_rows = worksheet.get_all_values()
    current_row_count = len(current_rows)
    print(f"Last row number: {current_row_count}")

    new_rows = []
    edited_rows = []

    # Compare each row of the current and previous rows
    for i in range(current_row_count):
        if i >= len(previous_rows):
            # New row
            if all(current_rows[i][col] for col in [0, 2, 4]):  # Check if columns A, C, and E have data
                new_rows.append(current_rows[i])
        else:
            if all(current_rows[i][col] for col in [0, 2, 4]):  # Check if columns A, C, and E have data
                if current_rows[i] != previous_rows[i]:
                    # Edited row
                    edited_rows.append((current_rows[i][0], current_rows[i][2], current_rows[i][4]))  # Only select specified columns

    if new_rows:
        print(f"{len(new_rows)} new row(s) inserted:")
        send_rows_to_telegram_new(new_rows)

    if edited_rows:
        print(f"{len(edited_rows)} row(s) edited:")
        send_rows_to_telegram_edited(edited_rows)

    # Update the previous rows
    previous_rows = current_rows

    return previous_rows


# Function to send rows to Telegram
def send_rows_to_telegram_new(new_rows):
    message = ""
    for row_data in new_rows:
        formatted_data = f"{row_data[4]} {row_data[0]} ({row_data[2]})"  # Adjust the index based on the desired columns
        message += f"{formatted_data}\n"
    print(message)  # Modify this to send the message to Telegram
    # Send the message to the Telegram channel
    try:
        client_telethon.send_message('harnoli7', message)
        print("Message sent to Telegram")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Function to send rows to Telegram
def send_rows_to_telegram_edited(edited_rows):
    message = ""
    for row_data in edited_rows:
        formatted_data = f"{row_data[2]} {row_data[0]} ({row_data[1]})"  # Adjust the index based on the desired columns
        message += f"{formatted_data}\n"

    print(message)  # Modify this to send the message to Telegram
    # Send the message to the Telegram channel
    try:
        client_telethon.send_message('harnoli7', message)
        print("Message sent to Telegram")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Initial check for new rows
print("Initial check:")
previous_rows = worksheet.get_all_values()

# Start the Telethon client
with client_telethon:
    # Start checking for new rows every 5 seconds
    while True:
        print("Sleep time started.")
        time.sleep(70)
        print("Sleep time ended.")
        print("Checking for new rows...")
        previous_rows = check_for_new_rows_and_send(previous_rows)
