import asyncio
import aiohttp
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

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

def get_existing_asins(worksheet):
    """Get a set of existing ASINs in the sheet."""
    asins = set()
    for row in worksheet.get_all_values():
        asins.add(row[0])
    return asins

async def get_keepa_data(asins, domain):
    """Fetch Keepa data asynchronously for a list of ASINs for a specific domain."""
    url = f'https://api.keepa.com/product?key={api_key}&domain={domain}&asin=' + ','.join(asins) + '&stats=30&buybox=1'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_data = await response.json()
            return response_data['products']

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

def extract_data(product):
    """Extract relevant data from Keepa product data."""
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

def insert_data(worksheet, data):
    """Insert data into Google Sheets and print update."""
    batch_size = 100  # Adjust batch size based on your quota and needs
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        worksheet.append_rows([list(item.values()) for item in batch])
        print(f"Update: Data inserted into Google Sheet ({worksheet.title}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(15)  # Pause after each batch insert

async def process_deals(url, worksheet_name):
    """Process deals from a given URL asynchronously and update Google Sheets."""
    print(f'Processing deals for {worksheet_name}...')
    response = await fetch_data(None, url)
    asins = [deal['asin'] for deal in response['deals']['dr']]
    worksheet = sheet.worksheet(worksheet_name)
    existing_asins = get_existing_asins(worksheet)
    new_data = []

    batch_size = 50  # Adjust batch size based on API and performance requirements
    for i in range(0, len(asins), batch_size):
        batch_asins = asins[i:i + batch_size]
        tasks = []
        for domain in domains:
            tasks.append(get_keepa_data(batch_asins, domain))

        products = await asyncio.gather(*tasks)

        for asin in batch_asins:
            product_data = {}
            for product in products:
                for p in product:
                    if p['asin'] == asin:
                        product_data[p['asin']] = extract_data(p)
                        break

            if product_data:
                new_data.extend(list(product_data.values()))
                await asyncio.sleep(1)  # Add a small delay between each batch request to avoid rate limiting

    if new_data:
        insert_data(worksheet, new_data)

    print(f'Deals processing completed for {worksheet_name}')
    print('Pause for 30 seconds...')
    await asyncio.sleep(30)  # Pause between each cycle

async def main():
    usa_url = "https://api.keepa.com/deal?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&selection=%7B%22page%22%3A0%2C%22domainId%22%3A%221%22%2C%22excludeCategories%22%3A%5B%5D%2C%22includeCategories%22%3A%5B%5D%2C%22priceTypes%22%3A%5B1%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B20%2C2147483647%5D%2C%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C2147483647%5D%2C%22minRating%22%3A-1%2C%22isLowest%22%3Afalse%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Atrue%2C%22filterErotic%22%3Atrue%2C%22singleVariation%22%3Afalse%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B2%2C3%2C4%2C5%5D%7D"
    canada_url = "https://api.keepa.com/deal?key=277a5p3cih7dokukn13qnr2pp40i3vnb1mhctd3b9eeogq1ol9bh6012qbeelk5j&selection=%7B%22page%22%3A0%2C%22domainId%22%3A%226%22%2C%22excludeCategories%22%3A%5B%5D%2C%22includeCategories%22%3A%5B%5D%2C%22priceTypes%22%3A%5B1%5D%2C%22deltaRange%22%3A%5B0%2C2147483647%5D%2C%22deltaPercentRange%22%3A%5B20%2C2147483647%5D%2C%22salesRankRange%22%3A%5B-1%2C-1%5D%2C%22currentRange%22%3A%5B0%2C2147483647%5D%2C%22minRating%22%3A-1%2C%22isLowest%22%3Afalse%2C%22isLowest90%22%3Afalse%2C%22isLowestOffer%22%3Afalse%2C%22isOutOfStock%22%3Afalse%2C%22titleSearch%22%3A%22%22%2C%22isRangeEnabled%22%3Atrue%2C%22isFilterEnabled%22%3Atrue%2C%22filterErotic%22%3Atrue%2C%22singleVariation%22%3Afalse%2C%22hasReviews%22%3Afalse%2C%22isPrimeExclusive%22%3Afalse%2C%22mustHaveAmazonOffer%22%3Afalse%2C%22mustNotHaveAmazonOffer%22%3Afalse%2C%22sortType%22%3A1%2C%22dateRange%22%3A%220%22%2C%22warehouseConditions%22%3A%5B2%2C3%2C4%2C5%5D%7D"

    tasks = [
        process_deals(usa_url, 'USA Deals'),
        process_deals(canada_url, 'Canada Deals')
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
