#!/usr/bin/env python3
# coding: utf-8

import re
import sys
import json
from typing import Optional
import requests
from retrying import retry

headers = {
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
}
# Testing ID - Always live
# channel_id = "UCSJ4gkVC6NrvII8umztf0Ow"
# Production ID - minhealthnz
channel_id = "UCPuGpQo9IX49SGn2iYCoqOQ"


@retry(stop_max_attempt_number=3)
def get(url: str) -> Optional[str]:
    try:
        r = requests.get(url, headers=headers)
        return r.text
    except requests.RequestException:
        pass


def get_live_video_info_from_html(html: str) -> Optional[str]:
    """
    Extract video info from HTML of channel page.
    """
    # regex = r'{"itemSectionRenderer":{"contents":\[{"shelfRenderer":{"title":{"runs":\[{"text":"Live now".+?"content":{"expandedShelfContentsRenderer":{"items":(.+?),"showMoreText":{"runs":\[{"text":"Show more"}]}}}'
    # regex = r'"contents":\[{"channelFeaturedContentRenderer":{"items":(.+?}])}}],"trackingParams"'
    regex = re.search(r'var ytInitialData = ({".+?});</script>',html)
    if regex is None:
        print("Could not find JSON data in Youtube Result")
        return None
    json_items = json.loads(regex.group(1))
    
    extract = json_items["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelFeaturedContentRenderer"]["items"][0]["videoRenderer"]
    # print(extract)
    # print(json.dumps(json_items, indent=2, separators=(',', ': ')))
    # exit(0)

    if (extract['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['text']['accessibility']['accessibilityData']['label'] != 'LIVE'):
        print("Youtube says it's live, but it isn't...")
        return None

    return extract['videoId']

def check_channel_live_streaming(channel_id: str) -> Optional[str]:
    html = get(f'https://www.youtube.com/channel/{channel_id}/featured')
    if '"label":"LIVE"' in html:
        print("Channel Live")

        # video_info = get_live_video_info_by_channel_id(channel_id)
        video_info = get_live_video_info_from_html(html)
        return video_info
    elif "404 Not Found" in html:
        print("Channel Not Found")
    return None


def checkLive() -> Optional[str]:
    return check_channel_live_streaming(channel_id)

# usage: ./check_youtube.py youtube_channel_id
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print(checkLive())
        exit(1)

    channel_id = sys.argv[1]

    info = check_channel_live_streaming(channel_id)

    if info:
        # Same output format as
        # youtube-dl --get-id --get-title --get-description
        print("Video ID: ",info)
    else:
        print(f'No live streams for channel {channel_id} available now', file=sys.stderr)
        exit(1)