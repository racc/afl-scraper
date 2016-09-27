import scrapy
import os
import fnmatch

from lxml import etree

AFL_STAT_HEADER = ["#", "S_ON", "S_OFF", "T_NM", "P_NM", "KI", "MK", "HB", "DI", "GL", "BH",
              "HO", "TK", "RB", "IF", "CL", "CG", "FF", "FA", "BR", "CP", "UP", "CM",
              "MI", "1%", "BO", "GA", "%P"]

AFL_SUB_ON = " ↑"
AFL_SUB_OFF = " ↓"

class AflTablesSpider(scrapy.Spider):
    name = "afl_tables"
    allowed_domains = ["afltables.com"]
    start_urls = map(lambda x: "http://afltables.com/afl/seas/" + str(x) + ".html", range(1997, 2016))
    download_delay = 3

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


def convert_html_to_psv(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.html'):
            htmlpath = os.path.join(root, filename)
            psvdata = get_match_stats_psv(htmlpath)
            psvfilename = os.path.splitext(filename)[0] + ".psv"
            psvfile = os.path.join(root, psvfilename)
            print("Writing: " + psvfile)            
            with open(psvfile, 'wb') as fpsv:   
                fpsv.write(psvdata)

def get_match_stats_psv(html):
    parser = etree.HTMLParser()
    tree = etree.parse(html, parser)
    team_one_name = tree.xpath("//table[1]/tr[2]/td[1]/a/text()")[0]
    team_two_name = tree.xpath("//table[1]/tr[3]/td[1]/a/text()")[0]
    team_one_stats = get_team_stats(team_one_name, tree.xpath("//tbody")[0])
    team_two_stats = get_team_stats(team_two_name, tree.xpath("//tbody")[1])
    data = ["|".join(AFL_STAT_HEADER)]
    for stat in team_one_stats:
        data.append("|".join(stat))
        
    for stat in team_two_stats:
        data.append("|".join(stat))
    return "\n".join(data)

def get_team_stats(team_name, tbody):
    team_stats = []    
        
    for tr in tbody.xpath("tr"):
        p_stats = {}
        tds = tr.xpath("td")
        p_stats["#"] = str(tds[0].text).replace(AFL_SUB_ON, "").replace(AFL_SUB_OFF, "").strip()
        p_stats["S_ON"] = str((tds[0].text.find(AFL_SUB_ON) != -1).numerator)
        p_stats["S_OFF"] = str((tds[0].text.find(AFL_SUB_OFF) != -1).numerator)
        p_stats["T_NM"] = team_name
        p_stats["P_NM"] = tds[1].xpath("a")[0].text
        
        for i in range(2, 25):
            header_index = i + 3;
            header = AFL_STAT_HEADER[header_index]
            p_stats[header] = tds[i].text.strip() if tds[i].text.strip() else "0"
        
        stats = map(lambda x: p_stats[x], AFL_STAT_HEADER)
        team_stats.append(stats)
    
    return team_stats
