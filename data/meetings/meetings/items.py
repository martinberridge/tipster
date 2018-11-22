# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MeetingItem(scrapy.Item):
   meeting_url = scrapy.Field() 
   meeting_name = scrapy.Field()   
   runners = scrapy.Field()

class RunnerItem(scrapy.Item):
   horse_url = scrapy.Field()
   horse_name = scrapy.Field()
   place = scrapy.Field()   
   age = scrapy.Field()
   last_ran = scrapy.Field()
