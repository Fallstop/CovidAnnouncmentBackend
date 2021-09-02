# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import sys
from dotenv import load_dotenv
from typing import Optional


load_dotenv()  # take environment variables from .env.


import googleapiclient.discovery
import googleapiclient.errors

api_key = os.environ["GCLOUD_API_KEY"]

if api_key is None:
    print("GCLOUD_API_KEY (Youtube API key) missing from env or .env file")
    sys.exit(1)

api_service_name = "youtube"
api_version = "v3"

# Get credentials and create an API client
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=api_key)

# Testing ID - Always live
# channel_id = UCSJ4gkVC6NrvII8umztf0Ow
# Production ID - minhealthnz
channel_id = "UCPuGpQo9IX49SGn2iYCoqOQ"

def checkLive() -> Optional[str]:

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        maxResults=1,
        type="video"
    )
    response = request.execute()

    if len(response["items"]) > 0:
        print("Channel is Live!")
        try:
            return response["items"][0]["id"]["videoId"]
        except Exception:
            print("Failed to get Youtube Livesteam")
    else:
        print("Channel not live")
        return None

if __name__ == "__main__":
    print("Check Live")
    print(checkLive())