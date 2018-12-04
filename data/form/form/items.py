# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field 

class HorseItem(Item) : 
    horse_url = Field()
    horse_name = Field()
    form = Field()

class FormItem(Item) :
    sp = Field()
    race_class = Field() 
    meeting_url = Field()
    place = Field()
    draw = Field()
    going = Field()
    distance = Field()
    horse_class = Field()
    url_jockey = Field()
    stone = Field()
    pounds = Field()
    behind_by = Field()
    meeting_date_time = Field()
    course = Field()
    commentary = Field()
    jockey_claim = Field()
    jockey_url = Field()
    trainer_url = Field()