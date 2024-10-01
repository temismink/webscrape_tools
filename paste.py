"""Selenium script that gets all the zip folder urls"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options

options = Options()
options.binary_location = "/usr/bin/google-chrome"  # Adjust the path if necessary
options.add_argument("--headless")  # Enable headless mode
options.add_argument("--no-sandbox")  # Required in some environments
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
options.add_argument("--remote-debugging-port=9222")

chrome_driver_path = "/home/ubuntu/myenv/lib/python3.10/site-packages/chromedriver_py/chromedriver_linux64"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Open the webpage
url = "https://multitracksearch.cambridge-mt.com/ms-mtk-search-ads.htm"
driver.get(url)

# Wait for the page to fully load (adjust the sleep time as necessary)
time.sleep(5)

# Simulate scrolling to load more content
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Get the page source after scrolling
html_content = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all the <a> tags that contain the zip folder links
zip_folder_links = soup.find_all("a", href=lambda href: href and href.endswith(".zip"))

# Check if any zip links are found
if not zip_folder_links:
    print("No zip links found on the page")
else:
    # Extract all zip folder links and store them in a list
    zip_folder_links_list = [link["href"] for link in zip_folder_links]

    # Print the list of zip folder links
    print(len(zip_folder_links_list), zip_folder_links_list)

# Close the browser when done
driver.quit()
