from util import hook
from atproto import Client, IdResolver
from datetime import datetime
from pytz import timezone

import re

bsky_re = (
    r"https?://bsky\.(?:app|social|network)/profile/[^/]+/post/([-_a-z0-9]+)",
    re.I,
)

@hook.api_key("bsky_user","bsky_token")
@hook.regex(*bsky_re)
def bsky_post(match, say=None, api_key=None):

    data = match.group()
    bsky_profile = data.split("/")[-3]
    post_id = data.split("/")[-1]

    client = Client()
    client.login(api_key["bsky_user"], api_key["bsky_token"])
    resolver = IdResolver()
    
    did = resolver.handle.resolve(bsky_profile)
    post = client.get_post(post_id, did)

    sane_time = datetime.strptime(post.value.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    sane_time = sane_time.astimezone(timezone('America/New_York')).strftime('%B %d, %Y %I:%M %p')

    reply = f"^ @{bsky_profile} - {post.value.text} - {sane_time}"

    return reply