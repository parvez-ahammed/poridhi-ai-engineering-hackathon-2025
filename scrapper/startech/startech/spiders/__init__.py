import scrapy
import re
from scrapy.selector import Selector

class StartechSpider(scrapy.Spider):
    name = "startech"
    allowed_domains = ["startech.com.bd"]
    start_urls = ["https://www.startech.com.bd"]

    def parse(self, response):
        # Extract category links from the navbar
        for nav_item in response.css('ul.navbar-nav li.nav-item.has-child'):
            parent_category = nav_item.css('a.nav-link::text').get().strip()
            for sub_category in nav_item.css('ul.drop-down li.nav-item a.nav-link'):
                sub_category_url = response.urljoin(sub_category.attrib['href'])
                sub_category_name = sub_category.css('::text').get().strip()
                yield response.follow(sub_category_url, callback=self.parse_category, meta={'parent_category': parent_category})

    def parse_category(self, response):
        # Extract product links and follow them
        for product in response.css("div.p-item a::attr(href)"):
            yield response.follow(product.get(), callback=self.parse_product, meta={'parent_category': response.meta['parent_category']})

        # Handle pagination by finding the "NEXT" button
        next_page = response.css("ul.pagination a:contains('NEXT')::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category, meta={'parent_category': response.meta['parent_category']})

    def parse_product(self, response):
        # Extract breadcrumb links for category
        breadcrumb_links = response.css(".breadcrumb a span[itemprop='name']::text").getall()
        # Category: Third-to-last item (e.g., "CPU Cooler")
        category = breadcrumb_links[-3].strip() if len(breadcrumb_links) >= 3 else None
        # Brand: Second-to-last item (e.g., "Deepcool")
        brand = breadcrumb_links[-2].strip() if len(breadcrumb_links) >= 2 else None

        # Extract short description, excluding "view-more" class
        short_description = [text.strip() for text in response.css(".short-description ul li:not(.view-more)::text").getall()]

        # Extract full description from the div with class "full-description"
        description_element = response.css("div.full-description")
        description = {}
        if description_element:
            headers = description_element.css("h2::text").getall()
            bodies_elements = description_element.css("p, ul, ol, div")
            bodies = []
            for element in bodies_elements:
                text = "".join(element.css("::text").getall()).strip()
                bodies.append(text)

            description = dict(zip(headers, bodies))

        # Extract SEO information
        seo_info = response.css("#latest-price p::text").get()
        #currency itemprop content="BDT" is not present in the provided HTML
        currency = response.css("meta[itemprop='priceCurrency']::attr(content)").get()

        price = response.css("meta[itemprop='price']::attr(content)").get()

        #extract specification table
        specification_table = {}
        tables = response.css("table.data-table.flex-table")
        for table in tables:
            headers = table.css("thead tr td.heading-row::text").get()
            if headers:
                specification_table[headers] = {}
                rows = table.css("tbody tr")
                for row in rows:
                    name = row.css("td.name::text").get()
                    value = "".join(row.css("td.value::text").getall()).strip()
                    if name:
                        specification_table[headers][name.strip()] = value.strip()

        # Extract image links from thumbnails
        image_links = [response.urljoin(a.attrib['href']) for a in response.css('ul.thumbnails li a.thumbnail')]

        # Yield the product details
        yield {
            "product_code": response.css(".product-code::text").get().strip() if response.css(".product-code::text").get() else None,
            "title": response.css("h1::text").get().strip() if response.css("h1::text").get() else None,
            "main_image": response.urljoin(response.css("img.main-img::attr(src)").get()) if response.css("img.main-img::attr(src)").get() else None,
            "gallery": image_links,
            "product_url": response.url,
            "price": price,
            "currency": currency,
            "brand": brand,
            "category": category,
            "parent_category": response.meta['parent_category'],
            "description": description,
            "short_description": short_description,
            "specification": specification_table
        }