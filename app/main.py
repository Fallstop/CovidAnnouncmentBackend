from fastapi import FastAPI
from datetime import datetime,timedelta,time
from time import sleep
from random import randrange
from typing import Optional
import threading
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from math import sin

from scrapper import scrape_website
from youtube_live import checkLive

app = FastAPI()

date_of_announcement: Optional[datetime] = None
youtube_live_id: Optional[str] = None


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
    return {"date_of_announcement": date_of_announcement}


@app.get(
    "/api/get_youtube_live",
    description="Checks if the min health nz youtube channel is streaming, if it is, it return the video ID, if not, it returns null.",
)
async def get_youtube_live():
    return {"youtube_video_id": date_of_announcement}

@app.get(
    "/api/fake_get_youtube_live",
    description="Fakes the /api/get_youtube_live with a hard coded 24/7 stream video id for testing",
)
async def fake_get_youtube_live():
    return {"youtube_video_id": "5qap5aO4i9A"}

# Background Tasks

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
            print("Waiting For tomorrow to scrape website")
            # We have the date for today, so just wait for tomorrow
            dt = datetime.now()
            tomorrow = dt + timedelta(days=1)
            tomorrow_time_delta = (datetime.combine(tomorrow, time.min) - dt)
            print((tomorrow_time_delta))
            sleep(tomorrow_time_delta.total_seconds())



"""
Background task to keep the youtube video api updated,
it's designed to keep Youtube Data API calls to a minium,
because we can only call it 100 times a day, aka every 15 minutes.

So we just don't update it when we don't think it will return anything interesting
"""
def youtube_live_task():
    global youtube_live_id
    while True:
        # Always check on start
        print("Checking if youtube Live")
        youtube_live_id = checkLive()

        # If the date isn't posted, we can assume
        # the video wouldn't be posted yet
        while date_of_announcement is None:
            # 42: The Answer to the Ultimate **Question** of Life, the Universe, and Everything.
            sleep(42)
        
        if youtube_live_id is None and date_of_announcement is not None:
            # We use a sine graph to get the current cache time,
            # It will cache for an hour at the opposite time of day,
            # and up to 30s at the announced time
            # https://www.desmos.com/calculator/wjsljmnmyx
            time_diff_announcement = abs(date_of_announcement - datetime.now()).total_seconds()/60/60
            cache_time = sin(time_diff_announcement/7.65)*59.5+0.5
            print("sleeping for",cache_time)
            sleep(cache_time*60)
        else:
            # Currently streaming, so we can chill a bit to every 5 minutes
            sleep(5*60)

scraper_daemon = threading.Thread(target=scraper_task, daemon=True)
scraper_daemon.start()

youtube_live_daemon = threading.Thread(target=youtube_live_task, daemon=True)
youtube_live_daemon.start()