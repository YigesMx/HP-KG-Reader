# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# coding=utf-8
from itemadapter import ItemAdapter
import json

class CrawlerPipeline:
    def __init__(self):
        self.file = open('harry_potter_property.json', 'w', encoding='utf-8')
        self.json = {}

    def process_item(self, item, spider):
        # line = '\"' + item['name'] + '\": ' + json.dumps(dict(item['property']), ensure_ascii=False) + ', \n'
        # self.file.write(line)
        self.json[item['name']] = dict(item['property'])
        return item

    def close_spider(self, spider):
        self.file.write(json.dumps(self.json, ensure_ascii=False))
        self.file.close()