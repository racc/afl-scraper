import scrapy

class AflTablesSpider(scrapy.Spider):
    name = "afl_tables"
    allowed_domains = ["afltables.com"]
    start_urls = map(lambda x: "http://afltables.com/afl/seas/" + str(x) + ".html", range(1997, 2016))

    def parse(self, response):
        for href in response.xpath('//a[contains(@href, "/stats/games")]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_game_stats)

    def parse_game_stats(self, response):
        round = str(response.xpath("//table[1]/tr[1]/td[2]/text()").extract()[0]).strip()
        season = str(response.xpath('//a[contains(@href, "/seas")]/text()').extract()[0])


        return ""
