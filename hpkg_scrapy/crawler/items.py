# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RelationItem(scrapy.Item):
    entity1 = scrapy.Field()
    entity2 = scrapy.Field()
    relation = scrapy.Field()


class PropertyItem(scrapy.Item):
    name = scrapy.Field()
    property = scrapy.Field()
