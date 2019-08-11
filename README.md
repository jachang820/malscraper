# MALScraper

Scrape [MAL](https://myanimelist.net/) for basic anime information using scrapy.py.

MALScraper successfully gets title, alternative titles, and information from the left sidebar, as well as related titles, voice actor and staff information from the details page, and the episode list from the episode page, and associated pictures. It scrapes each anime in sequence of its ID in MAL, starting from 1/Cowboy Bebop. 404 pages are skipped. Currently, there is somewhere north of 15,000 valid anime titles and 38,000 used and unused numbers. A JSON of scraped info and pictures are saved into folders by ID.

## Use

`scrapy crawl mal -a n=1000 images=4`

`n` is the number of valid titles to scrape, not including 404's. Due to scrapy being asynchronous, the actual number might slightly exceed what's specified. Last number stored will be scraped in `malscraper/output/latest.txt`. So if `latest = 400`, and `n = 250`, then the scraper will start at [401](https://myanimelist.net/anime/401) and continue scraping until [671](https://myanimelist.net/anime/671), since there are 21 numbers between 401-671 that are invalid (404's). *Default is 1000*.

`images` is the number of pictures per title to download. For example, if Naruto has 6 pictures under its [pictures page](https://myanimelist.net/anime/20/Naruto/pics), then the scraper will download the specified number of pictures if`images <= 6` or all 6 pictures. *Default is 4*.

## Built With

* [Scrapy 1.7.3](https://scrapy.org/) - Scraping framework for Python.

## Authors

* **Jonathan Chang** - *Initial work* - [jachang820](https://github.com/jachang820)
