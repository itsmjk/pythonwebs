import requests
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# Define your Keepa API key and domains
api_key = '277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j'
domains = [1, 6]  # 1 for US marketplace, 6 for CA marketplace

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('myjsonfile1.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheets document
sheet = client.open('Amazon')

def get_existing_asins(worksheet):
    """Get a set of existing ASINs in the sheet."""
    asins = set()
    for row in worksheet.get_all_values():
        asins.add(row[0])
    return asins

def get_keepa_data(asins):
    """Fetch Keepa data for a list of ASINs for both US and Canada domains using batch requests."""
    data = {}
    for domain in domains:
        url = f'https://api.keepa.com/product?key={api_key}&domain={domain}&asin=' + ','.join(asins) + '&stats=30&buybox=1'
        response = requests.get(url)
        response_data = response.json()
        for product in response_data['products']:
            asin = product['asin']
            if asin not in data:
                data[asin] = {}
            data[asin][domain] = product if 'products' in response_data and response_data['products'] else None
    return data

def format_price(price):
    """Format price to display."""
    if price in [-1, None]:
        return 'Not Available'
    return f"${price / 100:.2f}"

def format_percentage(percentage):
    """Format percentage to display."""
    if percentage in ['N/A', None, 'Not Available']:
        return 'Not Available'
    try:
        return f"{percentage:.1f}%"
    except ValueError:
        return 'Not Available'

def extract_data(products):
    """Extract relevant data from Keepa product data for both domains."""
    us_data = products[1] if products.get(1) else {}
    ca_data = products[6] if products.get(6) else {}
    
    def extract_product_data(product):
        stats = product.get('stats', {})
        monthly_sales = product.get('monthlySold', 'Not Available')
        current = stats.get('current', [])
        avg30 = stats.get('avg30', [])
        avg90 = stats.get('avg90', [])
        
        buybox = current[18] if len(current) > 18 and current[18] != -1 else current[1] if len(current) > 1 else 'Not Available'
        buybox30 = avg30[18] if len(avg30) > 18 and avg30[18] != -1 else avg30[1] if len(avg30) > 1 else 'Not Available'
        buybox90 = avg90[18] if len(avg90) > 18 and avg90[18] != -1 else avg90[1] if len(avg90) > 1 else 'Not Available'
        
        salesrank = current[3] if len(current) > 3 else 'Not Available'
        salesrank30 = avg30[3] if len(avg30) > 3 else 'Not Available'
        salesrank90 = avg90[3] if len(avg90) > 3 else 'Not Available'
        
        referral_fee = product.get('referralFeePercentage', 'Not Available')
        referral_fee = format_percentage(referral_fee)
        
        fba_fees = product.get('fbaFees', None)
        if fba_fees is None:
            fbafee = 'Not Available'
        else:
            fbafee = fba_fees.get('pickAndPackFee', 'Not Available')
            fbafee = format_price(fbafee) if fbafee != 'Not Available' else 'Not Available'
        
        return {
            'Monthly Sales': monthly_sales,
            'Buy Box': format_price(buybox),
            '30Buy Box': format_price(buybox30),
            '90Buy Box': format_price(buybox90),
            'Sales Rank': salesrank,
            '30Sales Rank': salesrank30,
            '90Sales Rank': salesrank90,
            'Referral Fee %': referral_fee,
            'FBA Fee': fbafee,
        }
    
    us_extracted = extract_product_data(us_data)
    ca_extracted = extract_product_data(ca_data)

    return {
        'ASIN': us_data.get('asin', 'Not Available') if us_data else ca_data.get('asin', 'Not Available'),
        'Title': us_data.get('title', 'Not Available') if us_data else ca_data.get('title', 'Not Available'),
        'US Monthly Sales': us_extracted['Monthly Sales'],
        'US Buy Box': us_extracted['Buy Box'],
        'US 30Buy Box': us_extracted['30Buy Box'],
        'US 90Buy Box': us_extracted['90Buy Box'],
        'US Sales Rank': us_extracted['Sales Rank'],
        'US 30Sales Rank': us_extracted['30Sales Rank'],
        'US 90Sales Rank': us_extracted['90Sales Rank'],
        'US Referral Fee %': us_extracted['Referral Fee %'],
        'US FBA Fee': us_extracted['FBA Fee'],
        'Canada Monthly Sales': ca_extracted['Monthly Sales'],
        'Canada Buy Box': ca_extracted['Buy Box'],
        'Canada 30Buy Box': ca_extracted['30Buy Box'],
        'Canada 90Buy Box': ca_extracted['90Buy Box'],
        'Canada Sales Rank': ca_extracted['Sales Rank'],
        'Canada 30Sales Rank': ca_extracted['30Sales Rank'],
        'Canada 90Sales Rank': ca_extracted['90Sales Rank'],
        'Canada Referral Fee %': ca_extracted['Referral Fee %'],
        'Canada FBA Fee': ca_extracted['FBA Fee'],
        'Date': datetime.now().strftime('%Y-%m-%d')
    }

def insert_data(worksheet, data):
    """Insert data into Google Sheets and print update."""
    batch_size = 100  # Adjust batch size based on your quota and needs
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        worksheet.append_rows([list(item.values()) for item in batch])
        print(f"Update: Data inserted into Google Sheet ({worksheet.title}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(15)  # Pause after each batch insert

def process_deals(url, worksheet_name):
    """Process deals from a given URL and update Google Sheets."""
    print('process 1')
    response = requests.get(url)
    data = json.loads(response.text)
    asins = [deal['asin'] for deal in data['deals']['dr']]
    print('process 2')
    worksheet = sheet.worksheet(worksheet_name)
    existing_asins = get_existing_asins(worksheet)
    new_data = []
    print('process 3')
    
    batch_size = 50  # Adjust batch size based on API and performance requirements
    for i in range(0, len(asins), batch_size):
        batch_asins = asins[i:i + batch_size]
        products = get_keepa_data(batch_asins)
        print('process 4')

        for asin in batch_asins:
            if asin in products:
                product_data = extract_data(products[asin])
                if product_data:
                    new_data.append(product_data)
                time.sleep(1)  # Add a small delay between each batch request to avoid rate limiting
    
    if new_data:
        insert_data(worksheet, new_data)
    print('process x')
    print('Pause of 20 seconds...')
    time.sleep(20)  # Pause after processing each URL

def main():
    usa_url = "https://api.keepa.com/deal?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&selection=%7B%22page%22%3A0%2C%22domainId%22%3A%221%22%2C%22excludeCategories%22%3A%5B%5D%2C%22includeCategories%22%3A%5B%5D%2C%22priceTypes%22%3A%5B1%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B20%2C2147483647%5D%2C%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C2147483647%5D%2C%22minRating%22%3A-1%2C%22isLowest%22%3Afalse%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Atrue%2C%22filterErotic%22%3Atrue%2C%22singleVariation%22%3Afalse%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B2%2C3%2C4%2C5%5D%7D"
    canada_url = "https://api.keepa.com/deal?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&selection=%7B%22page%22%3A0%2C%22domainId%22%3A%226%22%2C%22excludeCategories%22%3A%5B%5D%2C%22includeCategories%22%3A%5B%5D%2C%22priceTypes%22%3A%5B1%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B20%2C2147483647%5D%2C%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C2147483647%5D%2C%22minRating%22%3A-1%2C%22isLowest%22%3Afalse%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Atrue%2C%22filterErotic%22%3Atrue%2C%22singleVariation%22%3Afalse%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B2%2C3%2C4%2C5%5D%7D"
    
    while True:
        process_deals(usa_url, 'USA')
        process_deals(canada_url, 'CANADA')
        print('Pause for 30 seconds...')
        time.sleep(30)  # Pause between each cycle

if __name__ == "__main__":
    main()
