import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json, sys, csv, time
import scraper, helper
import kamernet

# Load environment variables from .env file
load_dotenv()
channels = {}

# Read JSON data from a file
with open('channels.json', 'r') as f:
    channels = json.load(f)

location = os.getenv("SEARCH_LOCATION")

# Define csv headers
scrapeContentKeys = ['city', 'title', 'url', 'platform', 'post_date', 'aantal_huurders', 'leeftijd', 'geslacht', 'bezigheid', 'huurprijs_pm']

for channel in channels:
    channel_url = channel['url']
    url_template = channel["scrape_url"]

    if channel['name'] == 'Kamernet':
        max_rent_price = int(os.getenv("MAX_RENT_PRICE")) / 100
        # Replace the placeholders with the actual values using string formatting
        scrape_url = url_template.format(location=location, maxRent=str(max_rent_price), page = 1) # we need to use selenium here
        seleniumDriver = scraper.seleniumInit(scrape_url)

        # scrape 10 pages
        for i in range(1, 10):
            print(scrape_url)
            aria_label = 'pagina'

            if i > 1:
                aria_label = 'Ga naar pagina'

            # Find an element by its CSS selector and click it
            paginationSelector =  f'button[aria-label="{aria_label} {i}"]'
            updatedDriver = scraper.interactWithPageElem(seleniumDriver, paginationSelector)

            # No updates to make so break
            if not updatedDriver:
                print('break')
                break

            result_container = scraper.scrapeThroughSelenium(updatedDriver, channels[0]['target_class'])

            # Get all page results of the result container
            searchResults = result_container.findChildren()
            kamernet.scrapeResults(searchResults, scrapeContentKeys)

        seleniumDriver.quit() # After all pages are scraped exit driver
    else:
        print('unsupported channel')
        sys.exit()

csv_file_path = "data.csv" # Define the CSV file path
helper.convertCsvToExcel(csv_file_path, 'data.xlsx', scrapeContentKeys)