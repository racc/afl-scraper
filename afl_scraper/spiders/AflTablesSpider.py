import scrapy
import os

class AflTablesSpider(scrapy.Spider):
    name = "afl_tables"
    allowed_domains = ["afltables.com"]
    start_urls = map(lambda x: "http://afltables.com/afl/seas/" + str(x) + ".html", range(1997, 2016))
    download_delay = 10

    def parse(self, response):
        for href in response.xpath('//a[contains(@href, "/stats/games")]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_game_stats)

    def parse_game_stats(self, response):
        season = str(response.xpath('//a[contains(@href, "/seas")]/text()').extract()[0]).replace("Games", "").strip()
        round_num = str(response.xpath("//table[1]/tr[1]/td[2]/text()").extract()[0]).strip()
        team_one = str(response.xpath("//table[1]/tr[2]/td[1]/a/text()").extract()[0])
        team_two = str(response.xpath("//table[1]/tr[3]/td[1]/a/text()").extract()[0])

        filename = "data/" + season + "/" + round_num + "/" + team_one + "_vs_" + team_two + ".html"
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open (filename, 'wb') as f:
            f.write(response.body)

        return None
