#Claire Tinati
#January 23, 2018
"""Scrapy spider to crawl magiccards.info and get card data"""

import re
import scrapy



class MtgScraper(scrapy.Spider):
    name= "mtg"
    start_urls= [
        "https://magiccards.info/sitemap.html",
    ]

    def parse(self, response):
        for setPage in response.css("li a::attr(href)").re(r"/.*/en.html")[:1]:
            self.log("Found a link to set: %s" % setPage)
            yield response.follow(setPage, callback=self.parseSetPage)
        self.log("Finished following set links.")

    def parseSetPage(self, response):
        for cardPage in response.xpath("//tr[contains(@class, 'even') or contains(@class, 'odd')]/td/a/@href").extract():
            self.log("Found a link to card: %s" % cardPage)
            meta= response.meta.copy()
            meta["setName"]= str(response.css("h1::text").extract_first().strip())
            meta["setCode"]= str(response.css("h1 small::text").extract_first().split("/")[0])
            yield response.follow(cardPage, callback=self.parseCardPage, meta=meta)
        self.log("Finished following card links.")

    def parseCardPage(self, response):
        pricePage= response.css("td script").xpath("@src").extract_first()
        self.log("Found link to price page: %s" % pricePage)
        cardName= str(response.css("body table tr td span a::text").extract_first())
        meta= response.meta.copy()
        meta["cardName"]= cardName
        yield response.follow(pricePage, callback=self.parsePricePage, meta=meta)
        

    def parsePricePage(self, response):
        prices= re.findall("\$[0-9]+\.[0-9][0-9]", response.text)
        prices.sort(key=(lambda x: float(x[1:])))
        prices= map(lambda x: str(x), prices)
        yield {
            "Name": response.meta["cardName"],
            "Set":  response.meta["setName"],
            "Code": response.meta["setCode"],
            "Low":  prices[0],
            "Mid":  prices[1],
            "Hi":   prices[2],
        }
