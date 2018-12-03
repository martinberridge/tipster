import scrapy 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from form.items import HorseItem, FormItem

import re

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
            item['meeting_url'], horse_url, item['jockey_url'], item['trainer_url'] = resultsrow.xpath(CELL3_XPATH+'//a/@href').extract()    
            
            #if horse pulled up place string is '-' 
            place_string = resultsrow.xpath(CELL1_XPATH+'/text()').extract_first()
            item["place"] = None if place_string.strip() == '-'  else int(re.sub(r'\D',"",place_string))
            
            raw_draw = resultsrow.xpath(CELL1_XPATH+'/div/text()').extract_first()  
            item["draw"] = int(re.sub(r'\D',"",raw_draw)) if raw_draw else None

            going_distance_class = resultsrow.xpath(CELL2_XPATH+'/text()').extract()[1:]  
            if len(going_distance_class) == 2: 
               item['going'],  item['distance'] = going_distance_class
            else :
               item['going'],  item['distance'], item['race_class'] = going_distance_class

            # TODO get date and time of meeting convert to datetime 
            item['jockey_claim'] = resultsrow.xpath(CELL3_XPATH+'/span[@class="jockey-claim"]/text()').extract_first()     
            
            # TODO convert to weight in pounds 
            stone = resultsrow.xpath(CELL3_XPATH+'/span[@class="racecard-weight-st"]/text()').extract_first()   
            pounds = resultsrow.xpath(CELL3_XPATH+'/span[@class="racecard-weight-lb"]/text()').extract_first()             
            

            item['stone'] =   int(re.sub(r'\D',"", stone)) if stone else None
            item['pounds'] =  int(re.sub(r'\D',"", pounds)) if pounds else None          
            
            item['sp'] = resultsrow.xpath(CELL4_XPATH+'/text()[1]').extract_first()        
            
            #refactor 
            behind_by_raw = resultsrow.xpath(CELL4_XPATH+'/text()[2]').extract_first()  
            if behind_by_raw :
                if behind_by_raw == 'won': 
                    item['behind_by'] = 0.0
                elif behind_by_raw == 'Pulled Up':
                    item['behind_by'] = None
                else:         
                    try:
                        search = re.search(r'\d+\.\d+',behind_by_raw)
                    except TypeError:
                        print("behind by raw {0}".format(behind_by_raw))
                    behind_by_string = re.search(r'\d+\.\d+',behind_by_raw)[0] if search else None
                    item['behind_by'] = float(behind_by_string) if behind_by_string else None
            
            form.append(dict(item)) 

        horse_item['form'] = form

        return horse_item