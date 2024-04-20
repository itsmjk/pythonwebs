import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from telethon.sync import TelegramClient

# Define the scope of access and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('myjsonfile1.json', scope)
client = gspread.authorize(creds)

# Telegram API credentials
api_id = 24277666
api_hash = '35a4de7f68fc2e5609b7e468317a1e37'
session_name = 'sheet1'
telegram_group_id = -1002010661365

# Initialize a Telethon client
client_telethon = TelegramClient(session_name, api_id, api_hash)

# Open the Google Spreadsheet by title and worksheet by title
spreadsheet = client.open("[CURRENT] April 24 Inventory")
worksheet = spreadsheet.worksheet("Current inventory list")

# Flag to indicate initial run
initial_run = True

# Function to check for changes in specified columns and send them to Telegram
def check_for_changes_and_send(previous_data):
    current_data = worksheet.get_all_values()

    new_row_added = False
    inventory_zeroed = False
    messages = []

    for current_row in current_data:
        # Check if a new row is added with at least three columns filled in
        if len(current_row) >= 3 and len(current_row[0].strip()) > 0 and len(current_row[2].strip()) > 0 and len(current_row[4].strip()) > 0:
            new_row_added = True

        # Check if any inventory quantity is turned to 0
        if current_row and len(current_row) >= 4 and current_row[3].strip() == '0':
            inventory_zeroed = True

    if new_row_added or inventory_zeroed:
        formatted_messages = []
        for row in current_data:
            if row[0] and row[2] and row[3] and row[4]:  # Check if columns A, C, D, and E are not empty
                d_value = row[3]
                if any(c.isdigit() for c in d_value) and '+' in d_value or (d_value.replace('.', '', 1).isdigit() and float(d_value) > 0):
                    formatted_row = f"{row[4]} {row[0]} ({row[2]})"  # Adjust the index based on the desired columns
                    formatted_messages.append(formatted_row)

        messages = formatted_messages

    if messages and (not initial_run) and messages != previous_data:  # Check if there are changes and it's not the initial run
        print("Changes detected. Sending message to Telegram...")
        send_messages_to_telegram(messages)
        print("Messages sent to Telegram")

    return messages

# Function to send messages to Telegram
def send_messages_to_telegram(messages):
    try:
        # Construct the message string
        message = "\n".join(messages)
        # Split the message into chunks of maximum 4000 characters
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        
        for chunk in chunks:
            # print(chunk)
            client_telethon.send_message(telegram_group_id, chunk)  # Corrected line
            time.sleep(1)  # Add a small delay between messages to avoid rate limits
        
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Initial check for changes
print("Initial check for changes:")
previous_data = worksheet.get_all_values()

# Start the Telethon client
with client_telethon:
    # Start checking for changes every 70 seconds
    while True:
        print("Sleep time started.")
        time.sleep(100)
        print("Sleep time ended.")
        print("Checking for changes...")
        previous_data = check_for_changes_and_send(previous_data)
        initial_run = False  # Update the initial_run flag after the first iteration
