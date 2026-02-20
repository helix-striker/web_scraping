import requests
import urllib.parse
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import concurrent.futures
import pandas as pd

def get_source(url):
    try:
        # Add scheme if missing
        if not url.startswith('http'):
            url = 'http://' + url
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def get_description(session, url):
    response = session.get(url, headers={'Accept-Encoding': 'gzip'})
    soup = BeautifulSoup(response.content, "html.parser")
    description = soup.find('meta', {"name": "description"})["content"] if soup.find('meta', {"name": "description"}) else None
    return description


def get_title(session, url):
    headers = {'Accept-Encoding': 'gzip'}
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        content = response.content
        try:
            content = gzip.decompress(content, 16+gzip.MAX_WBITS)
        except gzip.error:
            pass
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('h1')
        return title.text if title else None


def get_page_info(url):
    page_info = {}
    response = get_source(url)
    if response is not None:
        soup = BeautifulSoup(response.content, 'html.parser')
        page_info['url'] = url
        page_info['title'] = soup.title.text if soup.title is not None else ''
        page_info['word_count'] = len(soup.get_text(strip=True).split())

        # Extract the description
        session = HTMLSession()
        description = get_description(session, url)
        page_info['description'] = description if description is not None else ''

        # Add a list to keep track of headings and their levels
        heading_levels = []

        # Find all the headings on the page
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            # Determine the heading level by the tag name (e.g. 'h1', 'h2')
            heading_level = heading.name

            # Add the heading level and text to the list
            heading_levels.append(f'{heading_level}: {heading.text.strip()}')

        # Join the heading levels into a string and add it to the page_info dict
        page_info['heading_levels'] = ','.join(heading_levels) if len(heading_levels) > 0 else ''

        return page_info



def scrape_google(query, num_results=10, location=None):
    # Format the query for the URL
    query = urllib.parse.quote_plus(query)

    # Format the URL with the query and location
    url = f"https://www.google.com/search?q={query}"
    if location:
        url += f"&uule=w+CAIQICI{location.replace(' ', '')}"

    try:
        # Create a session object
        session = HTMLSession()

        # Get the search results page
        response = session.get(url)

        # Find the search result links and remove unwanted links
        links = list(response.html.absolute_links)
        google_domains = ('https://www.google.',
                          'https://google.',
                          'https://webcache.googleusercontent.',
                          'http://webcache.googleusercontent.',
                          'https://policies.google.',
                          'https://support.google.',
                          'https://maps.google.',
                          'https://www.youtube.',
                          'https://translate.google.')
        links = [link for link in links if not link.startswith(google_domains)]

        return links[:num_results]

    except Exception as e:
        print("Error fetching Google search results:", e)
        return []

#
# Take input from the user
query = input("Enter a query: ")
num_results = int(input("Enter the number of results to retrieve: "))

# Scrape Google search results
results = scrape_google(query, num_results=num_results)

# Get page information for each search result
page_info_list = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_url = {executor.submit(get_page_info, url): url for url in results}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            page_info = future.result()
            page_info_list.append(page_info)
        except Exception as e:
            print(f"Error getting page info for {url}: {e}")

# Create a DataFrame from the page information
df = pd.DataFrame(page_info_list)