import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import PyPDF2
import io
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
"""
This function uses beautiful soup to extract the text from a given page.

Parameters:
    url: The url of the page with the desired text

Returns:
    text: The text on the given page
    url: The url of the page
"""
def pageTextExtract(url):
    # Get response from the server
    response = requests.get(url)
    print(url)
    if response.status_code == 500:
        print("Server error")
        return
    if response.headers['Content-Type'] == 'application/pdf':
        pdf = io.BytesIO(response.content)
        pdfReader = PyPDF2.PdfReader(pdf)

        text = ""

        for pageN in range(len(pdfReader.pages)):
            page = pdfReader.pages[pageN]
            text += page.extract_text()

    else:
        # Parse the HTML 
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unneeded content on page
        for script in soup(["script", "style"]):
            script.extract()

        # Extract text in markdown format
        html = str(soup)
        html2text_instance = html2text.HTML2Text()
        html2text_instance.images_to_alt = True
        html2text_instance.body_width = 0
        html2text_instance.single_line_break = True
        text = html2text_instance.handle(html)

    return text, url

"""
This function takes a url and moves through all the links until it finds 
all the pages on the domain.

Parameters:
    url: the url of the domain you wish to get all the pages
    max_pages: The maximum number of pages to crawl

Returns:
    visited_pages: a list of unique pages beloning to the domain
"""
def get_all_pages(url, max_pages=2000):
    # Setup Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    driver = webdriver.Chrome(service=Service("C:\\Users\\bigba\\OneDrive\\Desktop\\chromedriver-win64\\chromedriver.exe"), options=options)
    
    pages_to_visit = [url] # List of URLs to visit
    visited_pages = set() # Set of already visited pages
    domain = urlparse(url).netloc # Extract domain to limit the crawling scope
    disallowed_extensions = re.compile(r'.*\.(pdf|jpg|jpeg|png|gif|svg|mp4|mp3|zip)$', re.IGNORECASE)
    
    try:
        while pages_to_visit and len(visited_pages) < max_pages:
            current_url = pages_to_visit.pop(0) # Get the next url to crawl

            #visited_pages.add(current_url)
            
            if current_url in visited_pages or disallowed_extensions.match(current_url) or "campus-life" in current_url:
                continue

            visited_pages.add(current_url)
            
            driver.get(current_url)

            #Wait for page to load
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))


            # Only process HTML content
            if 'text/html' not in driver.execute_script("return document.contentType;"):
                continue

            #visited_pages.add(current_url)
            
            # Get the links on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        full_url = urljoin(current_url, href) # Convert relative URLs to absolute URLs

                        # Make sure URL is from the same domain
                        if urlparse(full_url).netloc == domain and full_url not in visited_pages:
                            if not disallowed_extensions.match(full_url): # Skip non-html resoruces
                                pages_to_visit.append(full_url)
                                print(full_url)
                except Exception as e:
                    print(f"Error processing link: {e}")

            # Remove duplicates from the pages to visit
            pages_to_visit = list(set(pages_to_visit))

    finally:
        driver.quit()

    return list(visited_pages)

"""
This function takes a list of urls, and outputs their text contents into 
a text file.

Parameters:
    links: a list of urls
"""
def linkToText(links): 
    # Get current directory
    cwd = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(cwd, "MacewanData.txt")

    # Open the text file to write to
    with open(filepath, "w", encoding='utf-8') as file:
        for link in links:
            # Get the text contents from the page
            text = pageTextExtract(link)
            page_text = text[0] # Take the page text

            # Find header before this
            startpage = "\n\n__" 
            # Find footer before this
            endpage = "Treaty Six Territory\nWe acknowledge that the land"

            start_index = page_text.find(startpage) # Find header
            # If there is a header on the page remove it
            if start_index != -1:
                page_text = page_text[start_index:].strip()

            end_index = page_text.find(endpage) # Find footer
            # If there is a footer on the page remove it
            if end_index != -1:
                page_text = page_text[:end_index]

            # Add splitter between lines 
            file.write(page_text)
            file.write(text[1] + "\n" + "="*80 + "\n")   

            

if __name__ == "__main__":
    start_time = time.time()
    pages = get_all_pages("https://www.macewan.ca", 4000)
    end_time = time.time()
    duration_seconds = end_time - start_time
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    print(f"Pages found: {pages}")
    print(f"Pages found: {len(pages)}")
    print(f"Completed in {hours} hours and {minutes} minutes")

    linkToText(pages)

    # all_links = linkCrawler("https://www.macewan.ca",None,1)
    
    # print("\nAll pages found:")
    # for link in sorted(all_links):
    #     print(link)
    # print(f"Pages found: {len(all_links)}")
    # linkToText(all_links)

    # import os
    # print(os.access(os.getcwd(), os.W_OK))
    # print(os.getcwd())

    # for link in all_links:
    #     if "pdf" not in link:
    #         print("------------")
    #         print(link)
    #         print("------------")
    #         plip = pageTextExtract(link)
    #         print("============")
    #         print(plip[0])
    #         print("************")
    #         print(plip[1])
    #         print("============")

    # link = "https://calendar.macewan.ca/pdf/2024-2025N.pdf"
    # plip = pageTextExtract(link)
    # print(plip[0])
    # print(plip[1])



