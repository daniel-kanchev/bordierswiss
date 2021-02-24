import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bordierswiss.items import Article


class BordierswissSpider(scrapy.Spider):
    name = 'bordierswiss'
    allowed_domains = ['bordier.swiss']
    start_urls = ['https://www.bordier.swiss/actualites/']

    def parse(self, response):
        links = response.xpath('//a[@itemtype="https://schema.org/CreativeWork"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url or 'jpg' in response.url or 'mp4' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//text()').getall() or response.xpath('//h2//text()').getall()
        if not title:
            return
        title = [text for text in title if text.strip()]
        title = "\n".join(title).strip()

        date = response.xpath('//div[@class="elementor-widget-container"]/div[@class="elementor-text-editor'
                              ' elementor-clearfix"]/p/text()').get()
        if date:
            date = date.strip()
            if not date.split()[-1].isnumeric():
                date = ''
            else:
                date = " ".join(date.split()[-3:])
        elif not response.xpath('//h1//text()').getall():
            date = response.xpath('//h2/text()').get().split()[0]
        else:
            date = ''

        content = response.xpath('//div[@class="elementor-inner"]//text()').getall() or \
                  response.xpath('//div[@itemprop="text"]//text()').getall()

        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
