# -*- coding: utf-8 -*-
import scrapy
import os
import json
from malscraper.items import ImageItem


class MalSpider(scrapy.Spider):
    name = 'mal'
    allowed_domains = ['myanimelist.net']
    start_urls = ['https://myanimelist.net/']
    path = './malscraper/output/'
    max_images_per_item = 4

    def start_requests(self):
        num = self.last_num()
        self.visited = 0

        # n is a command line parameter specifying number of valid titles to scrape.
        if not hasattr(self, 'n') or self.n is None or not self.n.isdecimal():
            self.n = 1000
        else:
            self.n = int(self.n)

        # images is a command line parameter specifying max images per title to scrape.
        if not hasattr(self, 'images') or self.images is None or not self.images.isdecimal():
            self.images = 4
        else:
            self.images = int(self.images)

        while self.visited < self.n:
            num += 1
            details = 'https://myanimelist.net/anime/{0}'.format(num)
            yield scrapy.Request(url = details, callback = self.parse_details)


    def parse_details(self, response):
        if "404 Not Found" not in response.xpath("normalize-space(//title/text())").get():
            self.visited += 1
            meta, json = self.setup_metadata(response)
            print("Parsing details... {0}.".format(json['num']))

            # Updates json.
            self.parse_titles(response, json)
            self.parse_information(response, json)
            self.parse_related(response, json)
            self.parse_actors(response, json)
            self.parse_staff(response, json)
            self.parse_opening(response, json)
            self.parse_ending(response, json)
            if meta['hasEpisodes']:
                episodes = '{0}/episode?offset=0'.format(meta['canonical'])
                yield scrapy.Request(url = episodes, 
                    callback = self.parse_episodes,
                    cb_kwargs = dict(num = meta['num'], json = json))
            else:
                self.save_data(meta['num'], json)

            if meta['hasPics']:
                pictures = '{0}/pics'.format(meta['canonical'])
                yield scrapy.Request(url = pictures, 
                    callback = self.parse_pictures,
                    cb_kwargs = dict(num = meta['num']))

        else:
            print("{0} is a 404.".format(response.url.split("/")[4]))

        # Store latest anime number on disk.
        num = int(response.url.split("/")[4])
        if self.last_num() < num:
            self.last_num(num)

            

    def parse_episodes(self, response, num, json):
        print("Parsing episodes... {0}.".format(num))
        if 'Episodes' not in json:
            json['Episodes'] = {}
        episode = response.css("table.episode_list.ascend tr:nth-child(2)")
        while episode.get():
            ep_num = episode.xpath("td[contains(@class, 'episode-number')]")
            ep_num = "0000{0}".format(ep_num.xpath("normalize-space()").get())[-4:]
            english = episode.xpath("normalize-space(td[@class='episode-title']/a)").get()
            japanese = episode.xpath("normalize-space(td[@class='episode-title']/span)").get()
            aired = episode.xpath("normalize-space(td[contains(@class, 'episode-aired')])").get()
            json['Episodes'][ep_num] = {
                'English': english,
                'Japanese': japanese,
                'Date': aired
            }

            episode = episode.xpath("following-sibling::*[1]")

        # Pagination
        url = response.url.split("=")[0]
        offset = int(response.url.split("=")[-1])
        pages = response.xpath("descendant::div[contains(@class, 'pagination')]")
        current_page = pages.xpath("a[contains(@class, 'current')]")
        next_page_link = current_page.xpath("following-sibling::a[1]/@href").get()
        if next_page_link:
            yield scrapy.Request(url = next_page_link, 
                callback = self.parse_episodes,
                cb_kwargs = dict(num = num, json = json))

        else:
            self.save_data(num, json)

    def parse_pictures(self, response, num):
        print("Parsing pictures... {0}.".format(num))
        pictures = response.xpath("//h2[contains(., 'Pictures')]")
        pictures = pictures.xpath("following-sibling::table[1]")
        pictures = pictures.xpath("descendant::div[@class='picSurround']/a/@href").getall()
        pictures = pictures[:self.images]
        yield ImageItem(image_urls = pictures, num = num)

    def setup_metadata(self, response):
        meta = {}
        meta['url'] = response.url
        meta['num'] = int(response.url.split("/")[4])
        json = self.load_data(meta['num']) or { 'num': meta['num'] }
        nav = response.xpath("//div[@id='horiznav_nav']/ul")
        meta['name'] = nav.xpath("li/a/@href").get().split('/')[-1]
        meta['canonical'] = "{0}/{1}".format(meta['url'], meta['name'])
        sections = nav.xpath("li").xpath("normalize-space()").getall()
        meta['hasEpisodes'] = 'Episodes' in sections
        meta['hasPics'] = 'Pictures' in sections
        return meta, json

    def parse_titles(self, response, json):
        main_title = response.xpath("normalize-space(//h1)").get()
        titles = response.xpath("//h2[contains(., 'Alternative Titles')]")
        json['Title'] = { 'Romaji': main_title }
        while True:
            titles = titles.xpath("following-sibling::*[1]")
            if titles.xpath("name()").get() == 'div':
                category = titles.xpath("span/text()").get()[:-1]
                data = titles.xpath("normalize-space()").get()
                data = data[data.find(":") + 2:]
                json['Title'][category] = data

            else:
                break

    def parse_information(self, response, json):
        info = response.xpath("//h2[contains(., 'Information')]")
        json['Information'] = {}
        while True:
            info = info.xpath("following-sibling::*[1]")
            if info.xpath("name()").get() == 'div':
                category = info.xpath("span/text()").get()[:-1]
                data = info.xpath("normalize-space()").get()
                data = data[data.find(":") + 2:]
                json['Information'][category] = data

            else:
                break

        if not json['Information']['Episodes']:
            json['Information']['Episodes'] = "1"

    def parse_related(self, response, json):
        related = response.xpath("//h2[contains(., 'Related Anime')]")
        related = related.xpath("following-sibling::table[1]")
        json['Related Anime'] = {}
        for row in related.xpath("tr"):
            category = row.xpath("td[1]/text()").get()[:-1]
            data = row.xpath("normalize-space(td[2])").get()
            json['Related Anime'][category] = data

    def parse_actors(self, response, json):
        characters = response.xpath("//h2[contains(., 'Characters & Voice Actors')]")
        characters = characters.xpath("following-sibling::div[1]")
        json['Voice Actors'] = {}
        for columns in characters.xpath("div"):
            for character in columns.xpath("table"):
                category = character.xpath("normalize-space(tr/td[2]/a)").get()
                data = character.xpath("normalize-space(tr/td[3]/table/tr/td/a)").get()
                json['Voice Actors'][category] = data

    def parse_staff(self, response, json):
        staff = response.xpath("//h2[contains(., 'Staff')]")
        staff = staff.xpath("following-sibling::div[1]")
        json['Staff'] = {}
        for columns in staff.xpath("div"):
            for person in columns.xpath("table"):
                categories = person.xpath("normalize-space(tr/td[2]/div)").get().split(', ')
                data = person.xpath("normalize-space(tr/td[2]/a)").get()
                for category in categories:
                    if category not in json['Staff']:
                        json['Staff'][category] = [data]

                    else:
                        json['Staff'][category].append(data)

    def parse_opening(self, response, json):
        opening = response.xpath("//h2[contains(., 'Opening Theme')]")
        opening = opening.xpath("following-sibling::div[1]")
        json['Opening Themes'] = {}
        for theme in opening.xpath("span"):
            text = theme.xpath("normalize-space()").get()
            if text[0] == '#':
                num = "00{0}".format(text[1:text.find(':')])[-2:]
                name = text[text.find(':') + 2:]

            else:
                num = "00{0}".format(len(json['Opening Themes']))[-2:]
                name = text

            eps_index = text.find("(ep")
            if eps_index >= 0:
                eps = name[eps_index + 1:-1] # Get episode numbers without parentheses.
                eps = eps[eps.find(' ') + 1:] # Remove 'eps'.
                name = name[:eps_index]
            
            else:
                eps = ""

            json['Opening Themes'][num] = {'Song': name}
            if eps:
                json['Opening Themes'][num]['Episodes'] = eps

    def parse_ending(self, response, json):
        ending = response.xpath("//h2[contains(., 'Ending Theme')]")
        ending = ending.xpath("following-sibling::div[1]")
        json['Ending Themes'] = {}
        for theme in ending.xpath("span"):
            text = theme.xpath("normalize-space()").get()
            if text[0] == '#':
                num = "00{0}".format(text[1:text.find(':')])[-2:]
                name = text[text.find(':') + 2:]

            else:
                num = "00{0}".format(len(json['Ending Themes']))[-2:]
                name = text

            eps_index = name.find("(ep")
            if eps_index >= 0:
                eps = name[eps_index + 1:-1] # Get episode numbers without parentheses.
                eps = eps[eps.find(' ') + 1:] # Remove 'eps'.
                name = name[:eps_index]
            
            else:
                eps = ""

            json['Ending Themes'][num] = {'Song': name}
            if eps:
                json['Ending Themes'][num]['Episodes'] = eps

    def last_num(self, num = -1):
        filename = "{0}latest.txt".format(MalSpider.path)
        mode = 'r' if int(num) < 0 else 'w'
        with open(filename, mode) as f:
            if mode == 'r':
                num = f.read()
                if not num.isnumeric():
                    print("HALP ME!!!!!!!!!!!!!")
                    num = 0
            else:
                f.write(str(num))

        return int(num)

    def save_data(self, num, json_object):
        output = "{0}{1}/".format(MalSpider.path, num)
        if not os.path.exists(output):
            os.mkdir(output)
        filename = "{0}data.json".format(output)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii = False, indent = 4)

    def load_data(self, num):
        filename = "{0}{1}/data.json".format(MalSpider.path, num)
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                json_object = json.load(f)
        else:
            json_object = {}

        return json_object

