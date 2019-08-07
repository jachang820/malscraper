# MALScraper

Scrape [MAL](http://myanimelist.com/) for basic anime information using scrapy.py.

MALScraper successfully gets title, alternative titles, and information from the left sidebar, as well as related titles, voice actor and staff information from the details page, and the episode list from the episode page, and associated pictures. It scrapes each anime in sequence of its ID in MAL, starting from 1/Cowboy Bebop. 404 pages are skipped. Currently, there is somewhere north of 15,000 valid anime titles and 38,000 used and unused numbers. A JSON of scraped info and pictures are saved into folders by ID.

## Built With

* [Scrapy 1.7.3](https://scrapy.org/) - Scraping framework for Python.

## Authors

* **Jonathan Chang** - *Initial work* - [jachang820](https://github.com/jachang820)
