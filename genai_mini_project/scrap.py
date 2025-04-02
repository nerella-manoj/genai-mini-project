import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def fetch_content(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load content
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

def clean_data(soup):
    for script in soup(['script', 'style', 'footer', 'header', 'nav', 'aside']):
        script.decompose()
    return soup.get_text(separator=' ', strip=True)

def scrape_website(url):
    print(f"Scraping {url}...")
    soup = fetch_content(url)
    cleaned_text = clean_data(soup)
    return cleaned_text

# Save results to CSV
# def save_to_csv(data, filename="company_details.csv"):
#     df = pd.DataFrame(data)
#     df.to_csv(filename, index=False)

if __name__ == "__main__":
    url = input("Enter the website URL: ")
    extracted_text = scrape_website(url)
    print("Extracted Content:\n", extracted_text)