import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json, sys, csv
import scraper, helper

# Load environment variables from .env file
load_dotenv()
channels = {}

# Read JSON data from a file
with open('channels.json', 'r') as f:
    channels = json.load(f)

channel = channels[1]
channel_url = channel['url']
location = os.getenv("SEARCH_LOCATION")

# Scrape search results
def scrapeResults(searchResults, scrapeContentKeys): 
    # Print or iterate over the searchResults
    for searchResult in searchResults:
        # Only for given location
        if location not in searchResult.text.lower():
            continue

        # Get advert url
        child_url_sub = searchResult.find('a', class_='listing-search-item__link--title')

        # skip broken links
        if not child_url_sub:
            continue

        child_url_sub = child_url_sub.get('href')
        advert_url = channel_url + child_url_sub
        print(advert_url)

        response = requests.get(advert_url)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        scrapedContent = {}

        # Assign empty values to the keys
        for key in scrapeContentKeys:
            scrapedContent[key] = '-'

        scrapedContent['city'] = location

        # Get title
        scrapedContent['title'] = soup.find('h1', class_='listing-detail-summary__title').text 
        scrapedContent['kamer_type'] = helper.findRoomType(scrapedContent['title'])
        scrapedContent['url'] = advert_url
        scrapedContent['platform'] = channel['name']

        # Skip scraped searchResults
        if helper.checkCsvValueExists(os.getenv("CSV_FILE_PATH"), 'url', scrapedContent['url']):
            continue

        scrapedContent["post_date"] = helper.findSoup(soup, 'dd', 'listing-features__description--offered_since')
        scrapedContent["aantal_huurders"] = helper.findSoup(soup, 'dd', 'listing-features__description--maximum_number_of_tenants')
        scrapedContent["leeftijd"] = '-'
        scrapedContent["geslacht"] = '-'
        scrapedContent["doelgroep"] = helper.findSoup(soup,'dd', 'listing-features__description--required_statuses')
        price = helper.findSoup(soup, 'div', 'listing-detail-summary__price').strip()
        price = ' '.join(price.split()) # clear excessive whitespace
        scrapedContent["huurprijs_pm"] = price.replace(u'\xa0', u' ') # remove &nbsp

        # Remove all newlines
        for key in scrapedContent:
            scrapedContent[key] = scrapedContent[key].replace('\n', '')

        helper.writeToCsv(os.getenv("CSV_FILE_PATH"), scrapeContentKeys, list(scrapedContent.values()))