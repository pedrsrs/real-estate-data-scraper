import re
import csv
import scrapy
from scrapy.crawler import CrawlerProcess
from queue import Queue

class OlxSpider(scrapy.Spider):
    name = 'olx'
    start_url = 'https://www.olx.com.br/imoveis/venda/estado-sp/sao-paulo-e-regiao/centro'
    custom_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    MAX_RESULTS_PER_SEARCH = 5000
    MIN_PRICE = 0
    MAX_PRICE = 100000000

    def __init__(self):
        self.link_queue = Queue()  

    def start_requests(self):
        link = f'{self.start_url}?pe={self.MIN_PRICE + 1}&ps={self.MAX_PRICE}'
        self.link_queue.put(link)  

        if not self.link_queue.empty():
            yield scrapy.Request(self.link_queue.get(), headers=self.custom_headers, callback=self.parse_page)

    def parse_page(self, response):
        olx_result_number = re.search(
            r'de\s(.*?)\sresultados',
            response.css('.olx-text.olx-text--body-small.olx-text--block.olx-text--regular.olx-color-neutral-110::text').get().strip()
        )   
        if olx_result_number:
            unparsed_number_of_results = olx_result_number.group(1)
            number_of_results = unparsed_number_of_results.replace('.', '')

            if self.verify_result_size(int(number_of_results)):
                if int(number_of_results) > 0:
                    data = {
                        "url": response.url,
                        "qtd": number_of_results
                    }
                    self.write_to_csv(data)

            else:
                self.divide_links(response.url)

        if not self.link_queue.empty():
            next_link = self.link_queue.get()
            yield scrapy.Request(next_link, headers=self.custom_headers, callback=self.parse_page)

    def verify_result_size(self, number_of_results):
        return number_of_results <= self.MAX_RESULTS_PER_SEARCH
        
    def divide_links(self, url):
        min_price = int(re.search(r'pe=(\d+)', url).group(1))
        max_price = int(re.search(r'ps=(\d+)', url).group(1))
        half_point = (min_price + max_price) // 2 

        new_links = [
            f'{self.start_url}?pe={half_point + 1}&ps={max_price}',
            f'{self.start_url}?pe={min_price}&ps={half_point}'
        ]
        self.link_queue.queue.extendleft(new_links)
    
    def write_to_csv(self, data):
        with open('output.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["url", "qtd"])

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow(data)

process = CrawlerProcess()
process.crawl(OlxSpider)
process.start()
