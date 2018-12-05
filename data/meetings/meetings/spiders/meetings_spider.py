import scrapy 
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor  
from meetings.items import MeetingItem, RunnerItem

def date_urls(no_of_days):
   base = datetime.datetime.today()
   datelist = [base - datetime.timedelta(days=x) for x in range(0, no_of_days)]
   for d in datelist:
      yield d.strftime("https://gg.co.uk/racing/%d-%b-%Y").lower()


class MeetingsSpider(CrawlSpider):

    name = "meetings" 
    allowed_domains = ["gg.co.uk"]

    start_urls = date_urls(10)

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=['//*[@id="page"]//td[2]/a']),
            callback='parse_meeting'
        ),
    )

    def parse_meeting(self, response): 
      meeting_item = MeetingItem()
      meeting_item['meeting_url'] = response.request.url
      meeting_item['meeting_name'] = response.xpath('//h2/text()')[1].extract()  
      runners = []

      for runner in response.xpath('//table[@class="race-card "]//tr')[1:]   :
        runner_item = RunnerItem()
        runner_item['horse_url'] = runner.xpath('td[3]/a[1]/@href').extract_first()
        runner_item['horse_name'] = runner.xpath('td[3]/a[1]/text()').extract_first()
        runner_item['place'] =  runner.xpath('td[1]/text()[1]').extract_first()
        runner_item['age'],runner_item['last_ran'] = runner.xpath('td[2]/text()').extract()[-2:]  

        runners.append(dict(runner_item)) 
      meeting_item['runners'] = runners

      return meeting_item          