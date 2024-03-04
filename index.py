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

print(channels[0]['url'])

# sys.exit()  # Stop script execution
# URL of the website you want to scrape
# scrape_url = os.getenv("SCRAPE_URL")

location = os.getenv("SEARCH_LOCATION")
channel_url = channels[0]['url']
url_template = channels[0]["scrape_url"]
max_rent_price = int(os.getenv("MAX_RENT_PRICE")) / 100

# Replace the placeholders with the actual values using string formatting
scrape_url = url_template.format(location=location, maxRent=str(max_rent_price), page = '1') 

print(scrape_url)

target_div = scraper.scrapeUrl(scrape_url, channels[0]['target_class'])

# Print the content of the div
    
# Get all children of the target_div
searchResults = target_div.findChildren()

# Define the CSV file path
csv_file_path = "data.csv"

# Define csv headers
scrapedContentKeys = ['city', 'title', 'url', 'post_date', 'aantal_huurders', 'leeftijd', 'geslacht', 'bezigheid', 'huurprijs_pm']

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
    for key in scrapedContentKeys:
        scrapedContent[key] = '-'

    scrapedContent['city'] = location

    # Get title
    scrapedContent['title'] = soup.find('h3').text 
    scrapedContent['url'] = advert_url

    # Skip scraped searchResults
    if helper.checkCsvValueExists(csv_file_path, 'url', scrapedContent['url']):
        continue

    p_elems = soup.select('p') # get page p elems

    gNextFlag = False
    gFlagKey = "x"
    flagKeys = ["Aantal huurders", "Leeftijd", "Geslacht", "Bezigheid"]

    # Filter all p data
    for p_elem in p_elems:
        if gNextFlag:
            print(p_elem.text)
            scrapedContent[gFlagKey] = p_elem.text.replace(',', ' | ') # make sure no commas enter csv
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

    for h6_elem in h6_elems:
        if "€" in h6_elem.text:
            scrapedContent["huurprijs_pm"] = h6_elem.text.replace(u'\xa0', u' ') # remove &nbsp 
            break
    
    helper.writeToCsv(csv_file_path, scrapedContentKeys, list(scrapedContent.values()))
    print(scrapedContent)

    #sys.exit()  # Stop script execution

helper.convertCsvToExcel(csv_file_path, 'data.xlsx', scrapedContentKeys)
