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
    inventory_changed = False  # Flag to indicate if inventory quantity has changed
    messages = {}

    for current_row in current_data:
        # Check if a new row is added with at least three columns filled in
        if len(current_row) >= 3 and len(current_row[0].strip()) > 0 and len(current_row[2].strip()) > 0 and len(current_row[4].strip()) > 0:
            new_row_added = True

        # Check if any inventory quantity is turned from 0 to a value greater than 0 or vice versa
        if current_row and len(current_row) >= 4:
            previous_quantity = previous_data[current_row[0]][3] if current_row[0] in previous_data else None
            current_quantity = current_row[3].strip()
            if previous_quantity != current_quantity:
                # Check if either the previous or current quantity is not '0'
                if previous_quantity != '0' or current_quantity != '0':
                    inventory_changed = True
                    break

    if new_row_added or inventory_changed:
        categories = {}

        for row in current_data:
            if len(row) >= 5 and row[2]:  # Check if columns C is not empty
                keyword = row[2].strip().title()  # Title case the keyword for consistency
                try:
                    price = float(row[4].strip('$'))  # Convert price to float, remove dollar sign
                    if any(c.isdigit() for c in row[3]) and '+' in row[3] or (row[3].replace('.', '', 1).isdigit() and float(row[3]) > 0):
                        if keyword not in categories:
                            categories[keyword] = []
                        # Append the row based on price (lowest price first)
                        inserted = False
                        for i, item in enumerate(categories[keyword]):
                            item_price = float(item[4].strip('$'))
                            if price < item_price:
                                categories[keyword].insert(i, row)
                                inserted = True
                                break
                        if not inserted:
                            categories[keyword].append(row)
                except ValueError:
                    # Invalid price format, skip this row
                    continue

        messages = categories

    if messages and (not initial_run) and messages != previous_data:
        print("Changes detected.")
        messages_column_a = [message[0] for category, items in messages.items() for message in items]
        previous_data_column_a = [message[0] for category, items in previous_data.items() for message in items]
        # print("Messages Column A (messages):", messages_column_a)
        # print("Messages Column A (previous_data):", previous_data_column_a)
        
        if len(messages_column_a) == len(previous_data_column_a):
            if messages_column_a == previous_data_column_a:
                return messages
            else:
                send_messages_to_telegram(messages)
                print("Messages sent to Telegram")
                # Update previous_data with messages column A
                previous_data = {message: [] for message in messages_column_a}
        else:
            send_messages_to_telegram(messages)
            print("Messages sent to Telegram")
            # Update previous_data with messages column A
            previous_data = {message: [] for message in messages_column_a}

    return messages

def send_messages_to_telegram(messages):
    try:
        message = ""  # Initialize an empty message string
        for category, items in messages.items():
            message += f"{category.upper()}\n"
            valid_items = [item for item in items[1:] if item[4].strip('$').replace('.', '', 1).isdigit()]
            sorted_items = sorted(valid_items, key=lambda x: float(x[4].strip('$')))
            message += f"{items[0][4]} {items[0][0]} ({items[0][2]})\n"
            for item in sorted_items:
                message += f"{item[4]} {item[0]} ({item[2]})\n"
            message += '\n'
        
        # Check if the message exceeds the 4000 character limit
        if len(message) > 4000:
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for chunk in chunks:
                # client_telethon.send_message('harnoli7', chunk)
                client_telethon.send_message(telegram_group_id, chunk)  # Corrected line
                time.sleep(1)  # Add a small delay between messages to avoid rate limits
        else:
            # If the message is within the limit, send it as a single message
            # client_telethon.send_message('harnoli7', message)
            client_telethon.send_message(telegram_group_id, message)  # Corrected line
            time.sleep(1)  # Add a small delay between messages to avoid rate limits
    except Exception as e:
        print("An error occurred while sending messages to Telegram:", e)




# Initial check for changes
print("Initial check for changes:")
previous_data = worksheet.get_all_values()

# Start the Telethon client
with client_telethon:
    # Start checking for changes every 70 seconds
    while True:
        print("Sleep time started.")
        time.sleep(120)
        print("Sleep time ended.")
        print("Checking for changes...")
        previous_data = check_for_changes_and_send(previous_data)
        initial_run = False  # Update the initial_run flag after the first iteration
