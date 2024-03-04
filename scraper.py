import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from dotenv import load_dotenv
import os, json, sys, time

# Load environment variables from .env file
load_dotenv()

# Path to Chrome WebDriver executable
chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

"""
Scrape content from a designated page url with Selenium (bypass js limitations)

Args: 
    scrapeUrl (str): The url to be scraped 
    targetClass (str): The class that points to the content that needs to be scraped

Returns: Bs4 Object|Void

"""

def scrapeUrlThoroughly(scrapeUrl: str, targetClass: str):
    # Set up Selenium webdriver
    driver = webdriver.Chrome(executable_path=chromedriver_path)  # You need to have Chrome webdriver installed

    driver.get(scrapeUrl)  # Replace with your URL
    time.sleep(5)  # Allow time for JavaScript to execute
    html = driver.page_source  # Get the page source after JavaScript rendering

    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()   # Close the Selenium webdriver after data is retrieved

    target_div = soup.find('div', class_=targetClass)

    if not target_div:
        print("Couldn't find the specified div on the page.")
        sys.exit()  # Stop script execution
    
    return target_div


"""
Scrape content from a designated page url

Args: 
    scrapeUrl (str): The url to be scraped 
    targetClass (str): The class that points to the content that needs to be scraped

Returns: Bs4 Object|Void

"""

def scrapeUrl(scrapeUrl: str, targetClass: str):
    response = requests.get(scrapeUrl)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specific div you want to scrape by its class or ID
    target_div = soup.find('div', class_=targetClass)
    # target_div = soup.find('div', id='div_id')  # Example for finding by ID

    if not target_div:
        print("Couldn't find the specified div on the page.")
        sys.exit()  # Stop script execution
    
    return target_div

