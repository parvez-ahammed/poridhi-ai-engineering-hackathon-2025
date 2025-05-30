import scrapy
from .. items import StarTechItem # import items

class StarTechSpider(scrapy.Spider):
    """
    This Spider/Scraper/Crawler scrapes the "Star Tech BD" website
    Uncomment each link to scrape that category's products
    """
    name = "stSpider"
    start_urls = [
    #     'https://www.startech.com.bd/laptop-notebook', # Laptops-Notebooks
    #     'https://www.startech.com.bd/mobile-phone', # mobile phones
    #     'https://www.startech.com.bd/desktops', # desktops - DONE
    #     'https://www.startech.com.bd/component', # Desktop Components
    #     'https://www.startech.com.bd/tablet-pc', # tablet pc
    #     'https://www.startech.com.bd/camera', # camera
    #     'https://www.startech.com.bd/gaming', # gaming    
    #     'https://www.startech.com.bd/accessories', # accessories - BIG 4K+ 
    #     'https://www.startech.com.bd/server-networking', # server & storage
    #     'https://www.startech.com.bd/Security-Camera', # security cams
    #     'https://www.startech.com.bd/software', # softwares
    #     'https://www.startech.com.bd/television-shop', #tvs
    #     'https://www.startech.com.bd/gadget',# gadgets
    
    #     'https://www.startech.com.bd/networking', # networking
    #     'https://www.startech.com.bd/ups-ips', # ups 
    #     'https://www.startech.com.bd/monitor', # monitor
    #     'https://www.startech.com.bd/appliance', # appliances
    #     'https://www.startech.com.bd/office-equipment' # office equipments - start here
    ]

    # (1) - Extract individual Product's page links and follow them
    def parse(self, response):
        """
        This Function scrapes the url initial page and extracts the product urls and combines
        them with the root url
        
        Parameters-Variables : 
            response : [param] Stores the response 
        
        Returns
            yields
        """
        
        product_links = response.css('h4.p-item-name a').xpath("@href").extract()
        # print(f"total_num_products: {len(product_links)}") # DEBUG
        # print(product_links)  # DEBUG
        
        # product_links[0:1] for small testing
        for link in product_links: # arranges for each features for product
            full_url = response.urljoin(link) # Convert relative URL to absolute
            yield scrapy.Request(url=full_url, callback=self.parse_product) # Visit each product page
        
        # (3) - Traverse through all pages - next button / pagination
        next_page = response.css('ul.pagination li.active + li a::attr(href)').get() 
        
        if next_page is not None: # checks if next page exists, prevents scarping empty pages
            yield response.follow(next_page, callback = self.parse)
            
        
        
    # (2) - Extract Product details (name,price,description etc) from each individual product pages     
    def parse_product(self, response):
        """
        This Function scrapes the product details from each traversed individual product page 
        
        Parameters-Variables : 
            response : [param] Stores the response 
        
        Returns
            yields
        """
        
        # CREATE INSTANCE OF StarTechItem CLASS
        items = StarTechItem()
        
        product_name = response.css('h1.product-name::text').extract() 
        price = response.css('td.product-price ins::text, td.product-price::text').extract() 
        product_brand = response.css('td.product-brand::text').extract()
        product_key_features = response.css('div.short-description ul li::text').getall()
        product_specifications = response.css('#specification table thead tr td::text, #specification table tbody tr td::text').getall()
        product_description = response.css(
            'div.full-description h2::text, div.full-description h3::text, div.full-description p::text, #latest-price h2::text, #latest-price p::text'
            ).extract() 
        
        items['product_name'] = product_name
        items['price'] = price
        items['product_brand'] = product_brand
        items['product_key_features'] = product_key_features
        items['product_description'] = product_description
        items['product_specifications'] = product_specifications
        
        yield items
        
        ## uncommnet if items not used
        # yield {
        #     'product_name' : product_name,
        #     'price' : price,
        #     'product_brand' : product_brand,
        #     'product_key_features' : product_key_features,
        #     'product_description' : product_description,
        #     }
        
        # print(f"NUM OF PRODUCTS : {len(product_name)}") # DEBUG
        
        

        
        
        
        
        
       