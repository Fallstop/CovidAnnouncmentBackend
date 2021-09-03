from datetime import datetime,date
from random import randint, randrange
from time import sleep
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Optional


BASE_URL = "https://covid19.govt.nz"
NEWS_LIST = "/alert-levels-and-updates/latest-updates/"
ARTICLE_URL_PREFIX = "/alert-levels-and-updates/latest-updates/"
NEWS_LIST_FULL_URL = BASE_URL+NEWS_LIST+"?start="


def generate_keys(date) -> "tuple[str, str]":
    month_key = date.strftime("%B").lower()[0:3]
    day_key = str(date.day)
    return month_key,day_key

# Entry Point
def run_announcement_scraper(dates: List[datetime]) -> List[Optional[datetime]]:
    times: List[Optional[datetime]] = []
    
    # Controls the page of the news list to scrape
    current_pos_in_news = 0
    for date in dates:
        time = gather_articles(date,NEWS_LIST_FULL_URL+str(current_pos_in_news*10))
        if time is None:
            # Try moving to next page
            time = gather_articles(date,NEWS_LIST_FULL_URL+str((current_pos_in_news+1)*10))
            if time is not None:
                # Oh look it worked, lets do that for the rest
                current_pos_in_news += 1
        if time is not None:
            print("COULD NOT FIND ARTICLE")
        times.append(time)
        # Random delay to not spam there servers
        sleep(randrange(0,3))
    return times

def gather_articles(date: datetime, news_list_url: str)->Optional[datetime]:
    month_key,day_key = generate_keys(date)
    page = requests.get(news_list_url)
    
    soup = BeautifulSoup(page.content, "html.parser")
    all_page_links = soup.find_all('a')
    print("Using month key: ",month_key,"and day key:",day_key)

    final_result = None

    for link_element in all_page_links:
        link = link_element["href"]
        # Filter for article links
        if link.startswith(ARTICLE_URL_PREFIX):
            # Get Date Footer
            footer_of_article = link_element.parent.parent.parent.find("footer")
            # Filter for correct article
            if (footer_of_article is not None):
                date_of_article = str(footer_of_article.find("p")).lower()
                if (month_key in date_of_article and day_key in date_of_article):
                    print("Found latest article: ",link)
                    result = scanArticle(link, date)
                    if result is not None:
                        final_result = result
    return final_result

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