#Claire Tinati
#January 23, 2018
"""Scrapy spider to crawl magiccards.info and get card data"""

import re
import scrapy
import card_types



class MtgScraper(scrapy.Spider):
    #Scrapy vars
    name= "mtg"
    start_urls= [
        "https://magiccards.info/sitemap.html",
    ]
    #Text processing funcions
    def getType(self, s):
        pass


    #Scraping functions
    def parse(self, response):
        for setUrl in response.css("li a::attr(href)").re(r"/.*/en.html")[:1]:
            self.log("Found a link to set: %s" % setUrl)
            yield response.follow(setUrl, callback=self.parseSetPage)
        self.log("Finished following set links.")

    def parseSetPage(self, response):
        """Extract all cards from set page, along with card info.
           Card table cols: <ignore>, name/link, type, mana, rarity, artist, <ignore>."""
        for cardStr in response.xpath("//tr[contains(@class, 'even') or contains(@class, 'odd')]").extract():
            cardResp= scrapy.http.response.html.HtmlResponse(url="", body=cardStr.encode("utf-8"))
            cardUrl= cardResp.css("a::attr(href)").extract_first()
            self.log("Found a link to card: %s" % cardUrl)
            cardInfo= cardResp.css("td::text").extract()[1:-1]
            if len(cardInfo) == 3:    #Some cards have no cmc (ie: lands, xforms...)
                cardInfo.insert(1, None)
            meta= response.meta.copy()
            meta["cardName"]= str(cardResp.css("a::text").extract_first())
            meta["setName"]= str(response.css("h1::text").extract_first().strip())
            meta["setCode"]= str(response.css("h1 small::text").extract_first().split("/")[0])
            if len(cardInfo) != 4:
                self.log("WOAH WOAH WOAH card %s has a messed up chart! (len %d)" % (meta["cardName"], len(cardInfo)))
            meta["type"]= cardInfo[0].encode("utf-8")
            meta["mana"]= str(cardInfo[1])
            meta["rarity"]= str(cardInfo[2])
            meta["artist"]= str(cardInfo[3])
            yield response.follow(cardUrl, callback=self.parseCardPage, meta=meta)
        self.log("Finished following card links.")

    def parseCardPage(self, response):
        priceUrl= response.css("td script").xpath("@src").extract_first()
        self.log("Found link to price page: %s" % priceUrl)
        meta= response.meta.copy()
        yield response.follow(priceUrl, callback=self.parsePricePage, meta=meta)
        

    def parsePricePage(self, response):
        prices= re.findall("\$[0-9]+\.[0-9][0-9]", response.text)
        prices.sort(key=(lambda x: float(x[1:])))
        prices= map(lambda x: str(x), prices)
        yield {
            "Name":   response.meta["cardName"],
            "Set":    response.meta["setName"],
            "Code":   response.meta["setCode"],
            "Type":   response.meta["type"],
            "Mana":   response.meta["mana"],
            "Rarity": response.meta["rarity"],
            "Artist": response.meta["artist"],
            "Low":    prices[0],
            "Mid":    prices[1],
            "Hi":     prices[2],
        }
