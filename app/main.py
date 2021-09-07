from fastapi import FastAPI
from datetime import datetime, timedelta, time, date
import pause
from random import randrange
from typing import List, Optional
import threading
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from math import sin

from scrapper import run_announcement_scraper
from youtube_live_api import getHistoricVideos
from youtube_live_scrape import checkLive

app = FastAPI()

date_of_announcement: Optional[datetime] = None

HISTORY_LENGTH = 5
date_of_announcement_history: List[Optional[datetime]] = [None]*HISTORY_LENGTH
youtube_video_history: List[Optional[str]] = [None]*HISTORY_LENGTH


youtube_live_id: Optional[str] = None

date_of_announcement_overide_time = datetime.combine(
    date.today(), 
    time(13, 0))

ALLOWED_ORIGENS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGENS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/api/get-announcement-time",
    description="Gets the time for the media release for today. Will return an ISO8602 time, or the overide time if it hasn't been posted yet.",
)
async def api_get_announcement_time():
    return {"date_of_announcement": get_announcement_time()}


@app.get(
    "/api/get-historic-announcement-time",
    description="Gets the time for the media release for the past {} days (starting yesterday). Will return an array of ISO8602 time, or null if the scraper failed.".format(
        HISTORY_LENGTH),
)
async def api_get_historic_announcement_time():
    return {"dates_of_announcement": date_of_announcement_history}


@app.get(
    "/api/get-historic-youtube-live",
    description="Gets the video ID's for the media releases for the past {} days (starting yesterday). Will return an array of ISO8602 time, or null if failure, or not loaded yet.".format(
        HISTORY_LENGTH),
)
async def api_get_historic_youtube_live():
    return {"youtube_video_ids": youtube_video_history}


@app.get(
    "/api/get-youtube-live",
    description="Checks if the min health nz youtube channel is streaming, if it is, it return the video ID, if not, it returns null.",
)
async def api_get_youtube_live():
    return {"youtube_video_id": youtube_live_id}


@app.get(
    "/api/fake-get-youtube-live",
    description="Fakes the /api/get_youtube_live with a hard coded 24/7 stream video id for testing",
)
async def api_fake_get_youtube_live():
    return {"youtube_video_id": "5qap5aO4i9A"}

# Get Announcement Time
def get_announcement_time():
    if date_of_announcement is None:
        return date_of_announcement_overide_time
    else:
        return date_of_announcement


# Background Tasks

def today_announcement_task():
    global date_of_announcement
    while True:
        print("Starting website scrape")
        date_of_announcement = run_announcement_scraper([datetime.now()])[0]

        if date_of_announcement is None:
            # Wait ~ 15 minutes but a bit random just to stop
            # the bad kind of bot prevention scripts.
            pause.minutes((15+randrange(-1, 1)))
        else:
            # We have the date for today, so just wait for tomorrow
            dt = datetime.now()
            tomorrow = datetime.combine(dt + timedelta(days=1),time.min)
            print("Waiting For tomorrow to scrape website",tomorrow)
            pause.until(tomorrow)


def historic_data_collection_task():
    global date_of_announcement_history
    global youtube_video_history

    while True:
        print("Getting historic youtube videos")
        response = getHistoricVideos(HISTORY_LENGTH)
        if response is not None:
            youtube_video_history = response
        
        print("Starting historic website scrape")
        today = date.today()
        dates_to_check = []
        for i in range(1, HISTORY_LENGTH+1):
            dates_to_check.append(today - timedelta(days=i))
        date_of_announcement_history = run_announcement_scraper(dates_to_check)

        # doesn't need to update nearly as often, so we just update every 4.20 hours
        pause.hours(4.20)


"""`
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
        dt = datetime.now()

        # focal_point = get_announcement_time()
        
        time(hour=12)
        if youtube_live_id is None:
            if date_of_announcement is not None and dt < get_announcement_time():
                pause.seconds(30)
            elif dt < get_announcement_time():
                pause.minutes(2)
            else:
                pause.minutes(5)
        else:
            # Currently streaming, so we can chill a bit to every 5 minutes
            pause.minutes(5)


today_announcement_daemon = threading.Thread(
    target=today_announcement_task, daemon=True)
today_announcement_daemon.start()

historic_data_collection_daemon = threading.Thread(
    target=historic_data_collection_task, daemon=True)
historic_data_collection_daemon.start()


youtube_live_daemon = threading.Thread(target=youtube_live_task, daemon=True)
youtube_live_daemon.start()
