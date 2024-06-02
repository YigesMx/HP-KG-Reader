import scrapy
from ..items import RelationItem, PropertyItem
import re
from scrapy.selector import Selector


# class RelationSpider(scrapy.Spider):
#     name = "relation"
#     allowed_domains = ["fandom.com"]
#     start_urls = [
#         "https://harrypotter.fandom.com/zh/wiki/Category:%E4%BA%BA%E7%89%A9"
#     ]

#     def parse(self, response):
#         links = response.xpath("//ul[@class='category-page__members-for-char']/li/a/@href").extract()
#         for link in links:  # 遍历上个列表
#             if link.startswith('/zh/wiki/Category:'):
#                 url = 'https://harrypotter.fandom.com' + link
#                 yield scrapy.Request(url, callback=self.parse)
#             elif link.startswith('/zh/wiki/Template:'):
#                 pass
#             else:
#                 url = 'https://harrypotter.fandom.com' + link
#                 yield scrapy.Request(url, callback=self.parse_items)

#     def parse_items(self, response):
#         if len(response.xpath("//div[@class='portable-infobox pi-background pi-theme-wizard pi-layout-default']")
#                        .extract()) != 0:
#             current_name = response.xpath("//h1[@id='firstHeading']/text()").extract()[0]
#             header_list = response.xpath("//div[@class='pi-item pi-group pi-border-color']/div[1]/text()").extract()
#             for (idx, header) in enumerate(header_list):
#                 if header == '家庭信息':
#                     info_list = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]//ul/li"
#                                                .format(idx + 1)).extract()
#                     if len(info_list) == 0:
#                         info = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]"
#                                               "/div[2]/div[2]".format(idx + 1)).extract()[0]
#                         info = Selector(text=info)
#                         relation = "".join(info.xpath("//text()").extract())
#                         entity = info.xpath("//a/text()").extract()
#                         if len(relation) != 0 and len(entity) != 0:
#                             entity = re.sub(u"\\(.*?\\)", "", entity[0])
#                             relation = re.findall(r"[(](.*?)[)]", relation)
#                             if len(relation) != 0:
#                                 relation = relation[-1]
#                                 if relation == '可能':
#                                     relation = '可能存在关系'
#                                 item = RelationItem()
#                                 item['entity1'] = re.sub(u"\\(.*?\\)", "", entity[0])
#                                 item['entity2'] = current_name
#                                 item['relation'] = re.findall(r"[(](.*?)[)]", relation)
#                                 yield item
#                     else:
#                         for info in info_list:
#                             info = Selector(text=info)
#                             relation = "".join(info.xpath("//li/text()").extract())
#                             entity = info.xpath("//li/a/text()").extract()
#                             if len(relation) != 0 and len(entity) != 0:
#                                 entity = re.sub(u"\\(.*?\\)", "", entity[0])
#                                 relation = re.findall(r"[(](.*?)[)]", relation)
#                                 if len(relation) != 0:
#                                     relation = relation[-1]
#                                     if relation == '可能':
#                                         relation = '可能存在关系'
#                                     item = RelationItem()
#                                     item['entity1'] = re.sub(u"\\(.*?\\)", "", entity[0])
#                                     item['entity2'] = current_name
#                                     item['relation'] = re.findall(r"[(](.*?)[)]", relation)
#                                     yield item
#                 if header == '关系信息':
#                     info_list = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]"
#                                                .format(idx + 1))
#                     relation_list = info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
#                                                     "/div[1]/text()").extract()
#                     for idx, relation in enumerate(relation_list):
#                         if relation == '从属':
#                             entity_list = info_list.xpath(
#                                 "div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
#                                 "[{}]//ul/li/a/text()".format(idx + 1)).extract()
#                             if len(entity_list) == 0:
#                                 entity = info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
#                                                          "[{}]/div[2]/div[2]/a/text()".format(idx + 1)).extract()[0]
#                                 item = RelationItem()
#                                 item['entity1'] = current_name
#                                 item['entity2'] = entity
#                                 item['relation'] = relation
#                                 yield item
#                             else:
#                                 for entity in entity_list:
#                                     item = RelationItem()
#                                     item['entity1'] = current_name
#                                     item['entity2'] = entity
#                                     item['relation'] = relation
#                                     yield item
#                         if relation == '学院':
#                             item = RelationItem()
#                             item['entity1'] = current_name
#                             item['entity2'] = \
#                             info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
#                                             "[{}]//a/text()".format(idx + 1)).extract()[0]
#                             item['relation'] = relation
#                             yield item

class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["fandom.com"]
    start_urls = [
        "https://harrypotter.fandom.com/zh/wiki/Category:%E4%BA%BA%E7%89%A9"
    ]

    def parse(self, response):
        links = response.xpath("//ul[@class='category-page__members-for-char']/li/a/@href").extract()
        for link in links:  # 遍历上个列表
            if link.startswith('/zh/wiki/Category:'):
                url = 'https://harrypotter.fandom.com' + link
                yield scrapy.Request(url, callback=self.parse)
            elif link.startswith('/zh/wiki/Template:'):
                pass
            else:
                url = 'https://harrypotter.fandom.com' + link
                yield scrapy.Request(url, callback=self.parse_items)

    def parse_items(self, response):
        if len(response.xpath("//div[@class='portable-infobox pi-background pi-theme-wizard pi-layout-default']")
                       .extract()) != 0:
            item = PropertyItem()
            item['name'] = response.xpath("//h1[@id='firstHeading']/span/text()").extract()[0]
            property = {}
            header_list = response.xpath("//div[@class='pi-item pi-group pi-border-color']/div[1]/text()").extract()
            if '履历信息' not in header_list:
                return
            for (idx, header) in enumerate(header_list):
                if header == '家庭信息':
                    family_info = {}
                    info_list = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]//ul/li"
                                               .format(idx + 1)).extract()
                    if len(info_list) == 0:
                        info = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]"
                                              "/div[2]/div[2]".format(idx + 1)).extract()[0]
                        info = Selector(text=info)
                        relation = "".join(info.xpath("//text()").extract())
                        entity = info.xpath("//a/text()").extract()
                        if len(relation) != 0 and len(entity) != 0:
                            entity = re.sub(u"\\(.*?\\)", "", entity[0])
                            relation = re.findall(r"[(](.*?)[)]", relation)
                            if len(relation) != 0:
                                relation = relation[-1]
                                if relation == '可能':
                                    relation = '可能存在关系'
                                if relation not in family_info:
                                    family_info[relation] = entity
                                else:
                                    if type(family_info[relation]) == list:
                                        family_info[relation].append(entity)
                                    else:
                                        family_info[relation] = [family_info[relation], entity]
                    else:
                        for info in info_list:
                            info = Selector(text=info)
                            relation = "".join(info.xpath("//li/text()").extract())
                            entity = info.xpath("//li/a/text()").extract()
                            if len(relation) != 0 and len(entity) != 0:
                                entity = re.sub(u"\\(.*?\\)", "", entity[0])
                                relation = re.findall(r"[(](.*?)[)]", relation)
                                if len(relation) != 0:
                                    relation = relation[-1]
                                    if relation == '可能':
                                        relation = '可能存在关系'
                                    if relation not in family_info:
                                        family_info[relation] = entity
                                    else:
                                        if type(family_info[relation]) == list:
                                            family_info[relation].append(entity)
                                        else:
                                            family_info[relation] = [family_info[relation], entity]
                    property['家庭信息'] = family_info
                elif header == '关系信息':
                    info_list = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]"
                                               .format(idx + 1))
                    relation_list = info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
                                                    "/div[1]/text()").extract()
                    for idx, relation in enumerate(relation_list):
                        if relation == '学院':
                            property['学院'] = \
                            info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
                                            "[{}]//a/text()".format(idx + 1)).extract()[0]
                        else:
                            extracted_text = "".join(
                                info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
                                                "[{}]/div[2]//text()".format(idx + 1)).extract())
                            extracted_text = re.sub(u"\\[.*?\\]", "", extracted_text)
                            property[relation] = extracted_text.split('\n')[1:]
                elif header != '魔法特征信息':
                    info_list = response.xpath("//div[@class='pi-item pi-group pi-border-color'][{}]"
                                               .format(idx + 1))
                    relation_list = info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
                                                    "/div[1]/text()").extract()
                    for idx, relation in enumerate(relation_list):
                        if relation == '别称' or relation == '头衔' or relation == '签名':
                            continue
                        else:
                            extracted_text = "".join(
                                info_list.xpath("div[@class='pi-item pi-item-spacing pi-border-color pi-data']"
                                                "[{}]/div[2]//text()".format(idx + 1)).extract())
                            extracted_text = re.sub(u"\\[.*?\\]", "", extracted_text)
                            property[relation] = extracted_text.replace("\n", "")

            item['property'] = property
            if len(property) != 0:
                yield item
