from bs4 import BeautifulSoup as bs4
import requests
import pandas as pd

pages=[]
prices=[]
stars=[]
titles=[]
urlss=[]

#NO. of pages we want to scrape.
pages_to_scrape=2

#Loop for getting the page urls upto n.
for i in range(1,pages_to_scrape+1):
    url = ('http://books.toscrape.com/catalogue/page-{}.html').format(i)
    pages.append(url)
#print(pages)

#this block is to get all the html content from page one to page_to_scrape value.
for item in pages:
    page = requests.get(item)
    soup = bs4(page.text, 'html.parser')
#print(soup.prettify) #here is the html content of that page.

#this loop is for finding all the h3 tags in the html because titles of the items are in H3 tags. So while finding the titles on a perticular page we have to find title on html and then use findAll() function for getting titles.
    for i in soup.findAll('h3'):
        ttl=i.getText()
#print(tt1) #this line of code will print all the titles of that page because code is in for loop till all the h3 tags.
        titles.append(ttl)
#print(titles) #Now the titles are appended to titles and we can easily print titles of perticular page.

#This blog or loop will find all the p tags and class(price_colour) where price of each book is written, so as result we will get list of price of that page. 
    for j in soup.findAll('p', class_='price_color'):
        price=j.getText()
        prices.append(price)
#This block is for finding all the p tags and then with the use of (attrs Python method) 
    for s in soup.findAll('p', class_='star-rating'):
        for k,v in s.attrs.items():
            star =v[1]
            stars.append(star)
#this line of code is to find all the image container class in the html page because the url of image is in the src tag. 

    divs =soup.findAll('div', class_='image_container')
    for thumbs in divs:
        tgs=thumbs.find('img',class_='thumbnail')
        urls='http://books.toscrape.com/'+str(tgs['src'])
        newurls=urls.replace("../","")
        urlss.append(newurls)
data={'Title': titles, 'Prices': prices, 'Stars':stars, "URLs":urlss}
#print(data)
df=pd.DataFrame(data=data)
df.index+=1
df
#df.to_csv("/Users/mohit/Desktop/bookstore/output2.csv")