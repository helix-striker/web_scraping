import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs4

def get_source(url):
  

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def getDescription(url_list):
    info = []
    for url in url_list:
        with requests.get(url) as response:
            soup = bs4(response.text, "html.parser")
            description = soup.find('meta', {"name": "description"})["content"] if soup.find('meta', {"name": "description"}) else None
            info.append([description])
    return info


def getTitle(results):
     titles = []
     for item in results:
       page = requests.get(item)
       soup = bs4(page.content, 'html.parser')
       titl = soup.find('title')
       titles.append(titl)

     return titles


def scrape_google(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.com/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.',
                      'https://www.youtube.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)

    return links

results = []
title = []
description = []
queries = input('Search Keyword: ')
print("loading...")
results = scrape_google(queries)
title = getTitle(results)
description = getDescription(results)

data={'Title': title, "URLs": results, "Description": description}
df=pd.DataFrame(data=data)
df.index+=1

print(df)

#df.to_csv("/Users/mohitsharma/Desktop/bookstore/scrapedata.csv")