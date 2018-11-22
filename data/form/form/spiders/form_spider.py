import scrapy 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from form.items import HorseItem, FormItem

CELL1_XPATH = 'td[1]'
CELL2_XPATH = 'td[2]'
CELL3_XPATH = 'td[3]'
CELL4_XPATH = 'td[4]'

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

        print ( horse_item['horse_url'] )

        for result in response.xpath('//table[@id="results-profile"]/tbody'):
            
            formbody = result.xpath('tr') 
            resultsrow = formbody[0]
            commentaryrow = formbody[1]

            item = FormItem()
            
            item['commentary'] = commentaryrow.xpath('td/text()').extract_first()
            
            item["place"] = resultsrow.xpath(CELL1_XPATH+'/text()').extract_first()
            item["draw"]  = resultsrow.xpath(CELL1_XPATH+'/span/text()').extract_first()  
            going_distance_class = resultsrow.xpath(CELL2_XPATH+'/text()').extract()[1:]  
            if len(going_distance_class) == 2: 
               item['going'],  item['distance'] = going_distance_class
            else :
               item['going'],  item['distance'], item['race_class'] = going_distance_class

            item['meeting_url'], item['jockey_url'], item['trainer_url'] = resultsrow.xpath(CELL3_XPATH+'/a/@href').extract()    
            item['jockey_claim'] = resultsrow.xpath(CELL3_XPATH+'/span[@class="jockey-claim"]/text()').extract()     
            item['stone'] = resultsrow.xpath(CELL3_XPATH+'/span[@class="racecard-weight-st"]/text()').extract()     
            item['pounds'] = resultsrow.xpath(CELL3_XPATH+'/span[@class="racecard-weight-lb"]/text()').extract()             
            item['sp'] = resultsrow.xpath(CELL4_XPATH+'/text()[1]').extract_first()        
            item['behind_by'] = resultsrow.xpath(CELL4_XPATH+'/text()[2]').extract_first()        
            form.append(dict(item))

        horse_item['form'] = form

        return horse_item


