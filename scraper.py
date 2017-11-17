#scraper.py
#November 15, 2017
#Claire Tinati
"""Script to scrape magiccards.info to get all prices of cards in each set and display them."""

import re
import requests
import BeautifulSoup
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


#---------------------- Constants ----------------------
BASE_URL= "https://magiccards.info"
LANGUAGE= "en"
PRICE_TAGS= ["TCGPHiLoLow", "TCGPHiLoMid", "TCGPHiLoHigh"]
PRICE_NOT_FOUND_STR= ""

#----------------------- Classes -----------------------
class Price(object):
    """Class to model the prices for a mtg card.  Prices are strings encoding
         the USD price of the card, as "$X.XX".  Name is the card's name as
         a str."""
    def __init__(self, name, low, mid, high):
        self.name= name
        self.low= low
        self.mid= mid
        self.high= high

    def __str__(self):
        return "%s: %s, %s, %s" % (self.name, self.low, self.mid, self.high)

#---------------------- Functions ----------------------
def getPage(url):
    """Returns: unicode object containing raw <url> html, with JS loaded.
       Precondition: url is a str."""
    opts= Options()
    opts.add_argument("--headless")
    driver= webdriver.Chrome(chrome_options=opts)
    try:
        driver.get(url)
    except:
        print "Error: invalid url %s" % url
    src= driver.page_source
    driver.quit()
    return src


def makeSetPageUrl(setStr):
    """Returns: string encoding url for the landing page of the given set.
       Precondition: setStr is a str."""
    return "%s/%s/%s.html" % (BASE_URL, setStr.lower(), LANGUAGE)


def parseCardUrls(url, pageSrc):
    """Returns: list of strings encoding urls to individual cards from the set.
       Precondition: url is string built from BASE_URL; pageSrc is a string."""
    pageSrc= getPage(url)
    parser= BeautifulSoup.BeautifulSoup(pageSrc)
    cardUrlRegex= re.compile("%s/.*.html" % url[len(BASE_URL) : url.rfind(".")])
    rawTags= parser.findAll("a", {"href": cardUrlRegex})
    if len(rawTags) == 0:
        return "Error: set landing page %s is invalid."
    rawTags= map(lambda x: str(x), rawTags)
    cardUrls= map(lambda x: "%s%s" % (BASE_URL, x[x.find("\"")+1 : x.find(">")-1]), rawTags)
    for i in cardUrls:
        print i


def parsePrices(url, pageSrc):
    """Returns: filled Price object if pageSrc is valid; None otherwise
       Precondition: url is string built from BASE_URL; pageSrc is a string."""
    parser= BeautifulSoup.BeautifulSoup(pageSrc)
    #All cards have names: no name == invalid url
    name= str(parser.find("a", {"href": url[len(BASE_URL):]}))
    try:
        name= name[name.index(">")+1 : name.rindex("<")]
    except:
        print "Card at %s has no name, quitting early" % url
        return None
    lmh= map(lambda x: str(parser.find("td", {"class": x})), PRICE_TAGS)
    lmh= map(lambda x: re.search("\$[0-9]+\.[0-9]{2}", x), lmh)
    for i in range(len(lmh)):
        if lmh[i]:
            lmh[i]= lmh[i].group()
        else:
            lmh[i]= PRICE_NOT_FOUND_STR
    return Price(name, lmh[0], lmh[1], lmh[2])






def main():
    url= "https://magiccards.info/xln/en.html"
    pageSrc= getPage(url)
    parseCardUrls(url, pageSrc)
    #url= "https://magiccards.info/al/en/281.html"
    #pageSrc= getPage(url)
    #price= parsePrices(url, pageSrc)
    #print price



if __name__ == "__main__":
    main()

