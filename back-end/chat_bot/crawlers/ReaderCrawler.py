import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
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
from selenium.common.exceptions import TimeoutException
import time

"""
This function uses beautiful soup to extract the text from a given page.

Parameters:
    url: The url of the page with the desired text

Returns:
    text: The text on the given page
    url: The url of the page
"""
def pageTextExtract_bs4(url):
    # Get response from the server
    response = requests.get(url)
    #print(url)
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

            clean_url = strip_fragment(current_url)
            
            if clean_url in visited_pages or disallowed_extensions.match(current_url) or "campus-life" in current_url:
                continue

            visited_pages.add(clean_url)
            print(clean_url)
            
            driver.get(current_url)

            #Wait for page to load
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
            except TimeoutException:
                print(f"TimeoutException: No <a> tags found within 10 seconds for URL: {current_url}")
                continue


            # Only process HTML content
            if 'text/html' not in driver.execute_script("return document.contentType;"):
                continue

            # Get the links on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        full_url = urljoin(current_url, href) # Convert relative URLs to absolute URLs
                        full_url_cleaned = strip_fragment(full_url)

                        # Make sure URL is from the same domain
                        if urlparse(full_url_cleaned).netloc == domain and full_url_cleaned not in visited_pages:
                            if not disallowed_extensions.match(full_url_cleaned): # Skip non-html resoruces
                                pages_to_visit.append(full_url)
                                #print(full_url_cleaned)
                except Exception as e:
                    print(f"Error processing link: {e}")

            # Remove duplicates from the pages to visit
            pages_to_visit = list(set(pages_to_visit))

    finally:
        driver.quit()

    return list(visited_pages)


"""
This function takes a url and returns unnessesary elements from the url.

Parameters:
    url: the url of a page
"""
def strip_fragment(url):
    parsed_url = urlparse(url)
    # Return the link without unnessesary ending elements.
    return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, ''))

"""
This function takes a list of urls, and outputs their text contents into 
a text file.

Parameters:
    links: a list of urls
"""
def linkToText_new(links):
    # Get the current directory and path to text file
    cwd = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(cwd, "deebleData.txt")

    # Setup Selenium (Chrome) with headless option
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    service = Service("C:\\Users\\bigba\\OneDrive\\Desktop\\chromedriver-win64\\chromedriver.exe")  # Adjust to your Chromedriver path
    driver = webdriver.Chrome(service=service, options=options)

    # Helper function to process each link
    def process_link(link):
        # Use Selenium to fetch the page content
        driver.get(link)

         # Wait until the main content is loaded
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print(f"Error: Timeout loading {link}")
            return ""
        
        # Collect text from multiple tags
        text_elements = driver.find_elements(By.XPATH, "//p | //div | //span | //h1 | //h2 | //h3")
        page_text = "\n".join([element.text for element in text_elements if element.text.strip()])

        # Remove duplicate lines by converting text to a set, then back to a sorted list
        unique_lines = list(set(page_text.splitlines()))
        page_text = "\n".join(unique_lines)

        # Define header and footer identifiers
        startpage = "\n\n__" 
        endpage = "Treaty Six Territory\nWe acknowledge that the land"

        # Remove header if present
        start_index = page_text.find(startpage)
        if start_index != -1:
            page_text = page_text[start_index:].strip()

        # Remove footer if present
        end_index = page_text.find(endpage)
        if end_index != -1:
            page_text = page_text[:end_index]

        # Return text with at line seperator
        return f"{page_text}\n{link}\n{'=' * 80}\n"

    # Open the text file
    with open(filepath, "w", encoding='utf-8') as file:
        for link in links:
            print("Printing link: " + link)
            try:
                result = process_link(link)  # Get text from file
                file.write(result)  # Write to file
            except Exception as e:
                print(f"Error processing {link}: {e}")

    # Close the browser after all links are processed
    driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to initialize a single WebDriver and get text from one URL
def get_page_text_sel(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service("C:\\Users\\bigba\\OneDrive\\Desktop\\chromedriver-win64\\chromedriver.exe")  # Replace with the path to your chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    page_text = None
    try:
        print(f"Checking {url}")
        driver.get(url)
        #time.sleep(2)  # Wait for page to load; adjust if needed
        page_text = driver.find_element(By.TAG_NAME, "body").text
    except Exception as e:
        print(f"Error processing {url}: {e}")
    finally:
        driver.quit()
    
    return url, page_text

# Function to process a list of URLs concurrently
def get_text_from_multiple_pages(urls, output_file, max_workers=10):
    with open(output_file, "w", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all URL tasks to the executor
            future_to_url = {executor.submit(get_page_text_sel, url): url for url in urls}
            
            # As each task completes, write the result to the file
            for future in as_completed(future_to_url):
                url, text = future.result()
                if text:
                    f.write(f"URL: {url}\n")
                    f.write(f"Text:\n{text}\n")
                    f.write("="*80 + "\n")  # Separator line between entries
                else:
                    f.write(f"URL: {url}\n")
                    f.write("No text found or an error occurred.\n")
                    f.write("="*80 + "\n")  # Separator line between entries


def count_separator_in_file():
    """
    Counts the occurrences of the string '================================================================================'
    in a text file.

    Parameters:
        file_path (str): The path to the text file.

    Returns:
        int: The number of occurrences of the separator.
    """
    separator = "=" * 80  # Define the separator string
    count = 0

    cwd = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(cwd, "deebleData.txt")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                count += line.count(separator)
        return count
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

# Example usage:
# file_path = "example.txt"
# print(f"The separator appears {count_separator_in_file(file_path)} times.")




if __name__ == "__main__":
    # start_time = time.time()
    # pages = get_all_pages("https://www.macewan.ca/home", 3000)
    # end_time = time.time()
    # duration_seconds = end_time - start_time
    # hours = int(duration_seconds // 3600)
    # minutes = int((duration_seconds % 3600) // 60)
    # print(f"Pages found: {pages}")
    # print(f"Pages found: {len(pages)}")
    # print(f"Completed in {hours} hours and {minutes} minutes")
    # start_time_2 = time.time()
    # cwd = os.path.dirname(os.path.realpath(__file__))
    # filepath = os.path.join(cwd, "deebleData.txt")
    # texts = get_text_from_multiple_pages(pages, filepath, 5)
    # end_time_2 = time.time()
    # duration_seconds_2 = end_time_2 - start_time_2
    # hours_2 = int(duration_seconds_2 // 3600)
    # minutes_2 = int((duration_seconds_2 % 3600) // 60)
    # print(f"Pages found: {pages}")
    # print(f"Pages found: {len(pages)}")
    # print(f"Completed in {hours} hours and {minutes} minutes")
    # print(f"Completed in {hours_2} hours and {minutes_2} minutes")


    #urls = ["https://www.macewan.ca/academics/academic-departments/computer-science/our-people/profile/?profileid=elhajjm", "https://www.macewan.ca/academics/academic-departments/anthropology-economics-political-science/our-people/economics/profile/?profileid=liy257",  "https://www.macewan.ca/about-macewan/research/contact-us/"]

    link = "https://calendar.macewan.ca/pdf/2024-2025N.pdf"
    plip = pageTextExtract_bs4(link)

    cwd = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(cwd, "deebleData.txt")
    with open(filepath, "a", encoding='utf-8') as file:
        file.write(plip[0])
    print("DONE")

    #  pages = get_all_pages("https://www.macewan.ca/about-macewan/research/contact-us/", 1)
    #  print("*******************************")
    #  pages = get_all_pages("https://www.macewan.ca/about-macewan/research/contact-us/#collapse-id-597723", 1)

    # url_1 = "https://www.macewan.ca/about-macewan/research/contact-us/#collapse-id-597723"
    # print(url_1)
    # print(normalize_url(url_1))
    # print(strip_query_params(url_1))
    # print(strip_fragment(url_1))

    # url_2 = "https://www.macewan.ca/about-macewan/research/contact-us/profile/?profileid=kerrisonr2"
    # print(url_2)
    # print(normalize_url(url_2))
    # print(strip_query_params(url_2))
    # print(strip_fragment(url_2))

    #https://www.macewan.ca/about-macewan/research/contact-us/profile/?profileid=kerrisonr2
    #https://www.macewan.ca/about-macewan/research/contact-us/#collapse-id-597723
    #https://www.macewan.ca/about-macewan/research/contact-us/#collapse-id-914183    

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
    # print("hello")
    # plip = pageTextExtract_bs4(link)

    # print(plip[0])
    # print(plip[1])
    # print("heyo")



