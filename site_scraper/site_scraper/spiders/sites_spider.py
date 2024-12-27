from pathlib import Path

import scrapy

class SitesSpider(scrapy.Spider):
    name = "sites"

    def start_requests(self):
        urls = [
            "https://angelo.edu/"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"sites-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        