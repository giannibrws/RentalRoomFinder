import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json, sys, csv, time
import scraper, helper
import channels.kamernet as kamernet
import channels.pararius as pararius

# Load environment variables from .env file
load_dotenv()
channels = {}

# Read JSON data from a file
with open('channels.json', 'r') as f:
    channels = json.load(f)

location = os.getenv("SEARCH_LOCATION")

# Define csv headers
scrapeContentKeys = ['city', 'title', 'url', 'platform', 'post_date', 'kamer_type', 'aantal_huurders', 'leeftijd', 'geslacht', 'doelgroep', 'huurprijs_pm']
chromeDriverEnabled = scraper.chromeDriverEnabled()

for channel in channels:
    channel_url = channel['url']
    url_template = channel["scrape_url"]
    max_rent_price = os.getenv("MAX_RENT_PRICE")

    if channel['name'] == 'Kamernet' and chromeDriverEnabled:
        max_rent_price = int(max_rent_price) / 100
        # Replace the placeholders with the actual values using string formatting
        scrape_url = url_template.format(location=location, maxRent=str(max_rent_price), page = 1) # We need to use selenium here
        seleniumDriver = scraper.seleniumInit(scrape_url)

        # Scrape first 10 pages
        for i in range(1, 2):
            print(scrape_url)
            aria_label = 'pagina'
            cookie_policy_elem = 'div#onetrust-button-group-parent'

            if i > 1:
                aria_label = 'Ga naar pagina'

            # Skip cookies
            if (scraper.detectPageElem(seleniumDriver, cookie_policy_elem)):
                updatedDriver = scraper.interactWithPageElem(seleniumDriver, cookie_policy_elem, 2)

            # Find an element by its CSS selector and click it
            paginationSelector =  f'button[aria-label="{aria_label} {i}"]'
            updatedDriver = scraper.interactWithPageElem(seleniumDriver, paginationSelector)

            # No updates to make so break
            if not updatedDriver:
                print('break')
                break

            result_container = scraper.scrapeThroughSelenium(updatedDriver, channel['target_class'])

            # Get all page results of the result container
            searchResults = result_container.findChildren()
            kamernet.scrapeResults(searchResults, scrapeContentKeys)

        seleniumDriver.quit() # After all pages are scraped exit driver
    elif channel['name'] == 'Pararius':
        scrape_url = url_template.format(location=location, maxRent=str(max_rent_price))
        print(scrape_url)

        result_container = scraper.scrapeUrl(scrape_url, channel['target_class'], 'ul')
        searchResults = result_container.findChildren()
        pararius.scrapeResults(searchResults, scrapeContentKeys)
    else:
        print('unsupported channel')
        sys.exit()

helper.convertCsvToExcel(os.getenv("CSV_FILE_PATH"), 'data.xlsx', scrapeContentKeys)