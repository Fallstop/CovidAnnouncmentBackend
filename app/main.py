from fastapi import FastAPI
from datetime import datetime,timedelta,time
from time import sleep
from random import randrange
from typing import Optional
import threading
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


from scrapper import scrape_website

app = FastAPI()

date_of_announcement: Optional[datetime] = None


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/api/get-announcement-time",
    description="Gets the time for the media release for today. Will return an ISO8602 time, or null if it hasn't been posted yet.",
)
async def get_announcement_time():
    return [{"date_of_announcement": date_of_announcement}]


def scraper_task():
    global date_of_announcement
    while True:
        print("Starting website scrape")
        date_of_announcement = scrape_website(datetime.now())
        
        if date_of_announcement is None:
            # Wait ~ 15 minutes but a bit random just to stop
            # the bad kind of bot prevention scripts.
            sleep((15+randrange(-5,5))*60)
        else:
            print("Waiting For tomorrow")
            # We have the date for today, so just wait for tomorrow
            dt = datetime.now()
            tomorrow = dt + timedelta(days=1)
            tomorrow_time_delta = (datetime.combine(tomorrow, time.min) - dt)
            print((tomorrow_time_delta))
            sleep(tomorrow_time_delta.total_seconds())


scraper_daemon = threading.Thread(target=scraper_task, daemon=True)
scraper_daemon.start()