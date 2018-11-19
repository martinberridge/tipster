import scrapy 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from form.items import HorseItem, FormItem

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
        horse_item['horse_url'] = response.request.url
        horse_item['horse_name'] = response.xpath("//h1/text()").extract_first()
        form = []
        
        for result in response.xpath('//table[@id="results-profile"]/tbody'):
            meeting = result.xpath('tr//text()|tr//a/@href').extract()

            item = FormItem()
            
            item['meeting_url'] = meeting[9]
            item['place'] = meeting[0]
            item['draw'] = meeting[3]
            item['going'] = meeting[5]
            item['distance'] = meeting[6]
            item['horse_class'] = meeting[7]
            item['url_jockey'] = meeting[18]
            item['stone'] = meeting[15]
            item['pounds'] = meeting[16]
            item['behind_by'] = meeting[25]
            item['commentary'] = meeting[-1:][0]
            

            form.append(dict(item))

        horse_item['form'] = form

        return horse_item


