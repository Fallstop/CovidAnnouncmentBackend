# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import sys
from dotenv import load_dotenv
from typing import List, Optional
from collections import deque

from uritemplate.api import expand


load_dotenv()  # take environment variables from .env.

# LOG_NAME = os.environ["LOGGING_ENV"] if "LOGGING_ENV" in os.environ.keys()  else "development"
API_KEY = os.environ["GCLOUD_API_KEY"]
API_KEY_2 = os.environ["GCLOUD_API_KEY_2"]


import googleapiclient.discovery
import googleapiclient.errors
# from google.cloud import logging

# logging_client = logging.Client(credentials=API_KEY)



# logger = logging_client.logger(LOG_NAME)
# logger.log_text("Test")




if API_KEY is None or API_KEY_2 is None:
    print("GCLOUD_API_KEY (Youtube API key) missing from env or .env file")
    sys.exit(1)

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Get credentials and create an API client
youtube_1 = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
youtube_2 = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, developerKey=API_KEY_2)

youtube_active = deque([youtube_1,youtube_2])

# Testing ID - Always live
# channel_id = UCSJ4gkVC6NrvII8umztf0Ow
# Production ID - minhealthnz
channel_id = "UCPuGpQo9IX49SGn2iYCoqOQ"

def checkLive() -> Optional[str]:
    response = youtubeSearchWrapper(1)

    if response is not None and len(response["items"]) > 0:
        print("Channel is Live!")
        try:
            return response["items"][0]["id"]["videoId"]
        except Exception:
            print("Failed to get Youtube Livesteam")
    else:
        print("Channel not live")
        return None

def getHistoricVideos(max_results) -> Optional[List[Optional[str]]]:
    response = youtubeSearchWrapper(max_results)
    if (response is None):
        return None
    past_videos: List[Optional[str]] = list(map(lambda video: video["id"]["videoId"], response["items"]))
    print("Past Videos:",past_videos)
    return past_videos

def youtubeSearchWrapper(max_results, swap = False):
    request = youtube_active[0].search().list(
        part="snippet",
        channelId=channel_id,
        eventType="completed",
        maxResults=max_results,
        order="date",
        type="video"
    )
    try:
        return request.execute()
    except Exception as e:
        print("Exception",e)
        # Retry if the first time
        if not swap:
            youtube_active.rotate(1)
            return youtubeSearchWrapper(max_results,swap=True)
        else:
            youtube_active.rotate(-1)
            return None

if __name__ == "__main__":
    print("Check Live")
    print(checkLive())