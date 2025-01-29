"""
mfh stream stats
"""

import requests
import xmltodict
from util import hook, http, timesince


base_url = "http://stream.beanteam.org:8000/admin/stats"

@hook.api_key("mfh_stream")
@hook.command("mfh")
@hook.command("musicforhackers")
def get_info(inp, api_key=None):
    try:
        response = requests.get('http://stream.beanteam.org:8000/admin/stats', auth=('admin', api_key))
        data = xmltodict.parse(response.content)
        stream = data['icestats']['source']

        if isinstance(stream, dict):
            stream = [stream]

        target_stream = next((item for item in stream if item["@mount"] == '/mfh'), None)

        if target_stream:
            mfh_title = target_stream.get('title', 'Unknown Title')
            mfh_listeners = target_stream.get('listeners', '0')
            return(f"Now Playing: {mfh_title} - Listeners: {mfh_listeners} | http://stream.beanteam.org:8000/mfh")
        else:
            return("Stream Offline.")
    except:
        pass
