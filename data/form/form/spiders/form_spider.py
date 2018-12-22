import scrapy 
from scrapy.http import Request
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from form.items import HorseItem, FormItem
import datetime 
import re

CELL1_XPATH = 'td[1]'
CELL2_XPATH = 'td[2]'
CELL3_XPATH = 'td[3]'
CELL4_XPATH = 'td[4]'

def date_urls(no_of_days):
   base = datetime.datetime.today()
   datelist = [base - datetime.timedelta(days=x) for x in range(0, no_of_days)]
   for d in datelist:
      yield d.strftime("https://gg.co.uk/racing/%d-%b-%Y").lower()

class FormSpider(CrawlSpider):

    name = "form" 
    allowed_domains = ["gg.co.uk"]
    
    def __init__(self, no_of_days=1, *args, **kwargs):
        super(FormSpider, self).__init__(*args, **kwargs)
        self.start_urls = date_urls(int(no_of_days))

    start_urls = date_urls(10)
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

    def start_requests(self):
        for url in self.start_urls:
           yield Request(url)

    def parse_horse(self, response) :
        horse_item = HorseItem()
        horse_item['horse_url'] = "https://gg.co.uk/racing" + response.request.url
        horse_name_country = response.xpath("//h1/text()").extract_first()
        horse_item['horse_name']  = re.match('(.*)( \([A-Z]*\))', horse_name_country ).group(1).strip()
        form = []

        print ( horse_item['horse_url'] )

        for result in response.xpath('//table[@id="results-profile"]/tbody'):
            
            formbody = result.xpath('tr') 
            resultsrow = formbody[0]
            commentaryrow = formbody[1]

            item = FormItem()
            
            item['commentary'] = commentaryrow.xpath('td/text()').extract_first()
            meeting_url, horse_url, item['jockey_url'], item['trainer_url'] = resultsrow.xpath(CELL3_XPATH+'//a/@href').extract()    
            item['meeting_url'] = "https://gg.co.uk" + meeting_url
            r=re.search(r'([0-9]*)-([a-z]*)-([0-9]*).*\/([a-z]*).*-([0-9]*)',item['meeting_url'])
            dd, mon, yyyy, course, time = r.groups() 
            meeting_date_time =  datetime.datetime.strptime("{0} {1} {2} {3}:{4}".format(dd,mon,yyyy, time[:2],time[2:]),"%d %b %Y %H:%M")
            item['meeting_date_time'] = meeting_date_time
            item['course'] = course
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
            
            # refactor 
            behind_by_raw = resultsrow.xpath(CELL4_XPATH+'/text()[2]').extract_first()  
            if behind_by_raw :
                if behind_by_raw == 'won': 
                    item['behind_by'] = 0.0
                elif behind_by_raw == 'Pulled Up':
                    item['behind_by'] = None
                else:         
                    try:
                        search = re.search(r'\d+\.?\d+?',behind_by_raw)
                    except TypeError:
                        print("behind by raw {0}".format(behind_by_raw))
                    item['behind_by'] = float(search.group()) if search else None
            
            form.append(dict(item)) 

        horse_item['form'] = form

        return horse_item