# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request,FormRequest


class EplanningspiderSpider(Spider):
    name = 'eplanningSpider'
    allowed_domains = ['eplanning.ie']
    start_urls = ['http://eplanning.ie/']

    def parse(self, response):
        urls = response.xpath("//td/a/@href").extract()
        for url in urls:
            if "#" == url:
                pass
            else:
                yield Request(url,callback=self.parse_application, meta = {"url":url})

        print( url)
    
    def parse_application(self,response):
        application = response.xpath("//*[@class='glyphicon glyphicon-inbox btn-lg']/following-sibling::a/@href").extract_first()
        print(response.urljoin(application))
        yield Request(response.urljoin(application),callback=self.parse_form)
        pass

    def parse_form(self,response):
        yield FormRequest.from_response(response,formdata={     
            "RdoTimeLimit": "42"},
            dont_filter=True,
            formxpath="(//form)[2]",callback=self.parse_pages
        )

    def parse_pages(self,response):
        formurl = response.xpath("//td/a/@href").extract_first()
        
        for url in formurl:
            yield Request(response.urljoin(url),callback=self.parse_page)
        next_url= response.xpath("//*[@class='PagedList-skipToNext']/@href").extract_first()
        absolute_url = response.urljoin(next_url)
        yield Request(absolute_url,callback=self.parse_pages)
    def parse_page(self,response):
        style = response.xpath("//*[@value='Agents']/@style").extract_first()
        print(style)

        if style is None:
            self.logger.info("Does not have Agent button")

        elif "display: inline;  visibility: visible;" in style:
            #scrape that which needs to be scraped
            name = response.xpath("//tr[th='Name :']/td/text()").extract_first()
            address_first = response.xpath("//tr[th='Address :']/td/text()").extract_first()
            address_second = response.xpath("//tr[th='Address :']/following-sibling::tr/td/text()").extract()[0:3]
            address = address_first +address_second
            phone = response.xpath("//tr[th='Phone :']/td/text()").extract_first()
            fax = response.xpath("//tr[th='Fax :']/td/text()").extract_first()
            email = response.xpath("//tr[th='e-mail :']/td/a/text()").extract_first()
            url =response.url

            result = {
                "name":name,
                "address":address,
                "phone":phone,
                "fax":fax,
                "email":email,
                "url":url
            }

            yield result
        else:
            self.logger.info("Does not have Agent button")
        
        
