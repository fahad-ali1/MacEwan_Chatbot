import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import PyPDF2
import io
import re
import os
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
    pages_to_visit = [url]  # List of URLs to visit
    visited_pages = set()   # Set of already visited pages
    domain = urlparse(url).netloc  # Extract domain to limit the crawling scope
    disallowed_extensions = re.compile(r'.*\.(pdf|jpg|jpeg|png|gif|svg|mp4|mp3|zip)$', re.IGNORECASE)

    while pages_to_visit and len(visited_pages) < max_pages:
        current_url = pages_to_visit.pop(0)  # Get the next URL to crawl

        if current_url in visited_pages or disallowed_extensions.match(current_url):
            continue  # Skip if this page was already visited or is a non-HTML resource
        
        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()  # Ensure the page was retrieved successfully
        except requests.RequestException as e:
            print(f"Failed to retrieve {current_url}: {e}")
            continue

        # Only process HTML content
        if 'text/html' not in response.headers.get('Content-Type', ''):
            continue

        visited_pages.add(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the links on the page
        for link in soup.find_all('a', href=True):
            full_url = urljoin(current_url, link['href'])  # Convert relative URLs to absolute URLs

            # Make sure URL is from the same domain
            if urlparse(full_url).netloc == domain and full_url not in visited_pages:
                if not disallowed_extensions.match(full_url):  # Skip non-HTML resources
                    pages_to_visit.append(full_url)
                    print(full_url)

        # Remove duplicates from the pages to visit
        pages_to_visit = list(set(pages_to_visit))

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
    pages = get_all_pages("https://www.macewan.ca", 2000)
    print(f"Pages found: {pages}")
    print(f"Pages found: {len(pages)}")

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



