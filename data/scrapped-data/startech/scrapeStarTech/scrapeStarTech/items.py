# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class StarTechItem(scrapy.Item):
    product_name = scrapy.Field()
    price = scrapy.Field()
    product_brand = scrapy.Field()
    product_key_features = scrapy.Field()
    product_description = scrapy.Field()
    