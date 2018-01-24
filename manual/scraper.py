#scraper.py
#November 15, 2017
#Claire Tinati
"""Script to scrape magiccards.info to get all prices of cards in each set and display them."""

import re
import sys
import time
import requests
import BeautifulSoup
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


#---------------------- Constants ----------------------
SET_FILE_NAME= "sets_to_parse.txt"
SET_FILE_SELECT_LINE= "*"
BASE_URL= "https://magiccards.info"
SITEMAP_URL= "https://magiccards.info/sitemap.html"
LANGUAGE= "en"
PRICE_TAGS= ["TCGPHiLoLow", "TCGPHiLoMid", "TCGPHiLoHigh"]
PRICE_NOT_FOUND_STR= ""

#----------------------- Classes -----------------------
class MtgSet(object):
    """Class to contain the magiccards.info url and name of a mtg set,
         both as strs."""
    def __init__(self, url, name):
        self.url= url
        self.name= name
    def __str__(self):
        return "%s: %s" % (self.name, self.url)


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
    return cardUrls


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


def scrapeSet(setStr):
    """Returns: list of Price objects for all cards in the set if it's valid;
         empty list otherwise.
       Precondition: setStr is a str."""
    setPageUrl= makeSetPageUrl(setStr)
    print "Loading page %s..." % setPageUrl
    setPageSrc= getPage(setPageUrl)
    print "Parsing card urls..."
    cardUrls= parseCardUrls(setPageUrl, setPageSrc)
    cardPrices= []
    print "Scraping cards:"
    for cardUrl in cardUrls[:3]:
        sys.stdout.write("    Scraping a card...")
        sys.stdout.flush()
        cardPageSrc= getPage(cardUrl)
        cardPrices.append(parsePrices(cardUrl, cardPageSrc))
        sys.stdout.write("DONE\n")
    print "DONE"
    return cardPrices


def scrapeSetUrls():
    """Returns: list of urls corresponding to all magic sets."""
    print "loading sitemap..."
    sitemapSrc= getPage(SITEMAP_URL)
    print "Parsing set urls..."
    parser= BeautifulSoup.BeautifulSoup(sitemapSrc)
    setUrlRegex= re.compile("/.*/%s.html" % LANGUAGE)
    rawTags= parser.findAll("a", {"href": setUrlRegex})
    if len(rawTags) == 0:
        return "Error: cannot parse set urls from sitemap."
    rawTags= map(lambda x: str(x), rawTags)
    setUrls= map(lambda x: x[x.find("\"")+1 : x.find(">")-1], rawTags)
    setNames= map(lambda x: x[x.find(">")+1 : x.rfind("<")], rawTags)
    sets= [MtgSet(i[0], i[1]) for i in zip(setUrls, setNames)]
    return sets


def writeSetUrls(sets):
    """Writes a file in the current dir, with 1 line per set in the input.
       Precondition: sets is a list of MtgSet objects"""
    with open(SET_FILE_NAME, "w") as f:
        f.truncate()
        for mtgSet in sets:
            f.write("%s\n" % str(mtgSet))


def readSetUrls():
    """Reads the file in curr dir containing the sets to parse.
       Returns: list of MtgSet objects, one per line of the set url file that
         has been specifically tagged for scraping."""
    sets= []
    with open(SET_FILE_NAME, "r") as f:
        for line in f:
            if line[0] != SET_FILE_SELECT_LINE:
                continue
            print "Reading line: %s" % line
            parts= line.split(": ")
            sets.append(MtgSet(parts[1], parts[0]))
    return sets


def updateSetFile():
    sets= scrapeSetUrls()
    writeSetUrls(sets)




def main():
    #tStart= time.time()
    #cardPrices= scrapeSet("xln")
    #print "\n\n"
    #print "Scraping took %f sec to run" % (time.time() - tStart)
    #for price in cardPrices:
    #    print price
    sets= scrapeSetUrls()
    writeSetUrls(sets)



if __name__ == "__main__":
    if "update_sets" in sys.argv:
        print "Updating set url file..."
        updateSetFile()
    else:
        main()

