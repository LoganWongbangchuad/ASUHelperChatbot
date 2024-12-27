from pathlib import Path
import scrapy

class SitesSpider(scrapy.Spider):
    name = "sites"

    def start_requests(self):
        # Starting URL for the crawl
        urls = ["https://angelo.edu/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Create a folder named "scraped_pages" if it doesn't exist
        folder_path = Path("scraped_pages")
        folder_path.mkdir(exist_ok=True)

        # Save the current page in the folder
        page = response.url.split("/")[-2] or "index"
        filename = folder_path / f"sites-{page}.html"  # Save in the folder
        filename.write_bytes(response.body)

        self.log(f"Saved file {filename}")

        # Extract links and follow them
        for href in response.css("a::attr(href)").getall():
            # Convert relative links to absolute URLs
            link = response.urljoin(href)
            
            # Only follow links starting with angelo.edu
            if "angelo.edu" in link:
                yield scrapy.Request(url=link, callback=self.parse)
