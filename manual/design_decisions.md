1. Parsing
    -Needs:
        -extremely simple logic - three clearly-labeled tags per page
    -Used:
        -BeautifulSoup, due to extreme ease of use and lack of need for any advanced features.

2. Scraping
    -Needs
        -multiprocess scalable - low memory and cpu requirements
        -fast speed
        -handle extremely large number of pages (probably 20k+)
        -able to load javascript on each page
    -Consideration
        -Selenium
            -Pros
                -easy-to-use library
                -handles JS very well
            -Cons
                -seems to open a browser window on machine for each instance - not scalable
        -Scrapy
            -Pros
                -lots of advanced features
                -easy to scale
            -Cons
                -has trouble with JS without advanced support
    -Plan
        1)Try selenium at first, due to JS support
        2)Try switching to scrapy if parallelization becomes an issue
            -there may be a way to turn off the dummy browser, or have it use less resources
