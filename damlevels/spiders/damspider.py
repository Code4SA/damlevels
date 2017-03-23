import scrapy
from sodapy import Socrata


class RestrictionsSpider(scrapy.Spider):
    name = "restrictions"
    start_urls = [
        'https://www.westerncape.gov.za/general-publication/latest-western-cape-dam-levels',
    ]

    def parse(self, response):
        results = []
        items = response.xpath("//strong[contains(text(), 'Current water restrictions for Western Cape Municipalities')]")[0].xpath('following-sibling::ul')[0].xpath('li')

        for li in items:
            s = ' '.join(li.xpath('.//text()').extract())
            pre, post = s.split('-')

            results.append({
                'municipality': pre.strip(),
                'restrictions': post.strip(),
            })

        # save them
        self.save_items(results)

        # tell scrapy about them
        for item in results:
            yield item

    def save_items(self, items):
        if self.settings['SOCRATA_USERNAME'] and self.settings['SOCRATA_PASSWORD']:
            self.logger.info("Updating socrata with %s rows" % len(items))

            client = Socrata("data.code4sa.org", None, self.settings['SOCRATA_USERNAME'], self.settings['SOCRATA_PASSWORD'])
            client.replace("c2dq-tkgw", items)


class DamLevelSpider(scrapy.Spider):
    name = "damlevels"
    start_urls = [
        'https://www.dwa.gov.za/hydrology/weekly/ProvinceWeek.aspx?region=WC',
    ]

    def parse(self, response):
        results = []
        rows = response.css("#mainContent_tw tr")

        for row in rows[1:-1]:
            cells = row.xpath("./td")
            cells = [''.join(c.xpath(".//text()").extract()) for c in cells]
            # strip # chars and whitespace
            cells = [c.strip("#").strip() for c in cells]

            results.append({
                'dam': cells[0],
                'river': cells[1],
                'fsc': float(cells[4]),
                'this_week': float(cells[5]),
                'last_week': float(cells[6]),
                'last_year': float(cells[7]),
            })

        # save them
        self.save_items(results)

        # tell scrapy about them
        for item in results:
            yield item

    def save_items(self, items):
        if self.settings['SOCRATA_USERNAME'] and self.settings['SOCRATA_PASSWORD']:
            self.logger.info("Updating socrata with %s rows" % len(items))

            client = Socrata("data.code4sa.org", None, self.settings['SOCRATA_USERNAME'], self.settings['SOCRATA_PASSWORD'])
            client.replace("n6i8-b8c5", items)
