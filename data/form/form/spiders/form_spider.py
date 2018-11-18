import scrapy 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from form.items import HorseItem

class FormSpider(CrawlSpider):

    name = "form" 
    allowed_domains = ["gg.co.uk"]

    start_urls = ['https://gg.co.uk/racing/01-may-2018']
    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=['//*[@id="page"]//td[2]/a']),
            follow=True
        ), 

       Rule(
           LinkExtractor(restrict_xpaths=["//a[@class='horse']"]),
           callback='parse_horse'
       )
   
    )

    def parse_horse(self, response) :
        horse_item = HorseItem()
        horse_item['horse_name'] = response.xpath("//h1/text()").extract_first()
        return horse_item


