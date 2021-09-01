from datetime import datetime,date
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional


BASE_URL = "https://covid19.govt.nz"
NEWS_LIST = "/alert-levels-and-updates/latest-updates/"
ARTICLE_URL_PREFIX = "/alert-levels-and-updates/latest-updates/"


def generate_keys(date) -> "tuple[str, str]":
    month_key = date.strftime("%B").lower()[0:3]
    day_key = str(date.day)
    return month_key,day_key

def scrape_website(date) -> Optional[datetime]:
    month_key,day_key = generate_keys(date)


    page = requests.get(BASE_URL + NEWS_LIST)
    
    soup = BeautifulSoup(page.content, "html.parser")
    all_page_links = soup.find_all('a')
    print("Using month key: ",month_key,"and day key:",day_key)

    for link_element in all_page_links:
        link: str = link_element["href"]
        # Filter for article links
        if link.startswith(ARTICLE_URL_PREFIX):
            # Filter for correct article
            if (month_key in link and day_key in link):
                print("Found latest article: ",link)
                return scanArticle(link, date)

def scanArticle(link_suffix: str, date: datetime) -> Optional[datetime]:
    page = requests.get(BASE_URL + link_suffix)
    
    soup = BeautifulSoup(page.content, "html.parser")
    all_sections_title = soup.find_all(class_="content-element__title")
    
    filtered_locations_to_search = []

    for section in all_sections_title:
        if "media" in str(section).lower():
            filtered_locations_to_search += section.findParent().children

    for text in filtered_locations_to_search:
        result = re.search(r"([1-2]?[0-9])\s?([ap]m)",str(text),flags=re.IGNORECASE)
        if result is not None:
            print(result.groups())
            hour = int(result.groups()[0])
            if result.groups()[1].lower()=="pm":
                hour += 12
            return datetime(date.year,date.month,date.day,hour=hour)
    print("Could not find date, returning None")