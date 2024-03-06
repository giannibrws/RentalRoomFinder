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

channel = channels[0]
channel_url = channel['url']
location = os.getenv("SEARCH_LOCATION")
csv_file_path = os.getenv("CSV_FILE_PATH")

# Scrape search results
def scrapeResults(searchResults, scrapeContentKeys): 
    # Print or iterate over the searchResults
    for searchResult in searchResults:

        # Only for given location
        if location not in searchResult.text.lower():
            continue

        child_url_sub = searchResult.get('href') # Get advert url

        # skip broken links
        if not child_url_sub:
            continue

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
        scrapedContent['title'] = soup.find('h3').text 
        scrapedContent['url'] = advert_url
        scrapedContent['platform'] = channel['name']

        # Skip scraped searchResults
        if helper.checkCsvValueExists(csv_file_path, 'url', scrapedContent['url']):
            continue

        p_elems = soup.select('p') # get page p elems

        gNextFlag = False
        gFlagKey = "x"
        flagKeys = ["Aantal huurders", "Leeftijd", "Geslacht", "Bezigheid"]
        flagConversionKeys = {'doelgroep': 'bezigheid'}

        # Filter all p data
        for p_elem in p_elems:
            if gNextFlag:
                 # Get the key for the desired value using a dictionary comprehension
                key = next((key for key, value in flagConversionKeys.items() if value == gFlagKey), gFlagKey)
                print(p_elem.text)
                scrapedContent[key] = p_elem.text.replace(',', '|') # make sure no commas enter csv
                gNextFlag = False
                continue

            if " dagen " in p_elem.text:
                scrapedContent["post_date"] = p_elem.text
                print("Found dagen:", p_elem.text)
                continue
            elif " uur " in p_elem.text:
                print("Found uur:", p_elem.text)
                scrapedContent["post_date"] = p_elem.text
                continue
            
            for key in flagKeys:
                if key in p_elem.text:
                    print(f"Found '{key}' in p_elem.text:", p_elem.text)
                    gFlagKey = key.lower().replace(' ', '_') # convert to parsable key
                    gNextFlag = True
                    break

        h6_elems = soup.select('h6') # get page h6 elems
        room_tag_keys = ['Gestoffeerd ', 'Kaal ', 'Gemeubileerd ']
        f1 = f2 = False

        for h6_elem in h6_elems:
            if "€" in h6_elem.text:
                scrapedContent["huurprijs_pm"] = h6_elem.text.replace(u'\xa0', u' ') # remove &nbsp 
                f1 = True
            for room_tag_key in room_tag_keys:
                if room_tag_key in h6_elem.text:
                    scrapedContent["kamer_type"] = helper.findRoomType(h6_elem.text)
                    f2 = True
                    break
            if f1 and f2:
                break
        
        helper.writeToCsv(csv_file_path, scrapeContentKeys, list(scrapedContent.values()))
        print(scrapedContent)