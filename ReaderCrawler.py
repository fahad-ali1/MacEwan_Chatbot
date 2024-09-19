import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import time
import PyPDF2
import io
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
    if response.status_code == 500:
        print("Server error")
        return
    if response.headers['Content-Type'] == 'application/pdf':
        print("pdf")
        text = "what"

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
This function takes takes a website and recursively finds all the sites it links to.

Parameters:
    url: The url of the page with the desired text
    visited: A set of urls that have already been visited
    max_depth: The maximum page depth for the crawler to go to
    current_depth: The current page depth of the crawler

Returns:
    visited: The set of all urls visited by the crawler
"""
def get_all_links_2(url, visited=None, max_depth=2, current_depth=0):
    # Create visited set if this is the first url
    if visited is None:
        visited = set()
    
    # Avoid visiting the same URL multiple times
    if url in visited or current_depth > max_depth:
        return visited
    
    # Remove all campus-life urls and pdfs
    if "campus-life" in url or "pdf" in url:
        return visited

    # Add current url to visited
    visited.add(url)
    print(f"Visiting: {url}")

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()

        response.encoding = response.apparent_encoding
        content = response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return visited
    
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Find all anchor tags with href attributes
    for link in soup.find_all("a", href=True):
        # Join the base URL with the href to get an absolute URL
        href = urljoin(url, link.get("href"))
        # Keep only URLs that belong to the same domain
        if urlparse(href).netloc == urlparse(url).netloc:
            visited = get_all_links_2(href, visited, max_depth, current_depth + 1)

    # Add a delay to avoid overwhelming the server
    time.sleep(0.05)
    
    return visited

if __name__ == "__main__":
    # all_links = get_all_links_2("https://calendar.macewan.ca/academic-schedule/current/",None,1)
    
    # print("\nAll pages found:")
    # for link in sorted(all_links):
    #     print(link)
    # print(f"Pages found: {len(all_links)}")

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
    link = "https://calendar.macewan.ca/pdf/2024-2025N.pdf"
    plip = pageTextExtract(link)
    print(plip[0])
    print(plip[1])


