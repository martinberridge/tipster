import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
import logging

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        logging.log(logging.DEBUG, "process Item")
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            logging.log(logging.DEBUG, "inserting item")
            self.collection.insert(dict(item))
        return item
