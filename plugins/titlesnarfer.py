from __future__ import unicode_literals
from util import hook
from bs4 import BeautifulSoup
import requests
import re
import time

REGEX = r"(http|https)://(www.)?(?!(www.)?twitter|(www.)?youtube|bsky|youtu.be|(www.)?google|(en.)?wikipedia)[-a-zA-Z0-9@:%._\+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"

MAX_TITLE = 125
MAX_RECV = 1_000_000

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}

def _read_limited(r, limit=MAX_RECV, chunk=16384):
    buf = []
    size = 0
    for part in r.iter_content(chunk_size=chunk):
        if not part:
            break
        buf.append(part)
        size += len(part)
        if size >= limit:
            break
    return b"".join(buf)

def _looks_html(content_type):
    ctype = (content_type or "").lower()
    return "html" in ctype or "xml" in ctype or ctype == ""

def _extract_title(doc):
    # prefer og then twitter then <title>, finally a single h1
    og = doc.select_one("meta[property='og:title'][content]")
    if og and og.get("content"):
        t = og["content"].strip()
        if t:
            return t
    tw = doc.select_one("meta[name='twitter:title'][content]")
    if tw and tw.get("content"):
        t = tw["content"].strip()
        if t:
            return t
    if doc.title and doc.title.string:
        t = doc.title.string.strip()
        if t:
            return t
    h1 = doc.select_one("h1")
    if h1:
        t = h1.get_text(strip=True)
        if t:
            return t
    return None

def _clean_title(s):
    # collapse internal whitespace
    return " ".join(s.split())

@hook.regex(REGEX)
def titlesnarfer(match):
    url = match.group()

    # optional quick skip like your original pattern intended
    lower = url.lower()
    if any(x in lower for x in ("twitter.com", "x.com", "youtube.com", "youtu.be", "bsky.app", "google.", "wikipedia.org")):
        return

    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=(3.0, 5.0), allow_redirects=True) as r:
            # proceed even if not r.ok as long as body looks like html or xml
            if not _looks_html(r.headers.get("content-type")) and r.status_code >= 400:
                return

            content = _read_limited(r, MAX_RECV)
    except requests.ReadTimeout:
        return
    except requests.RequestException:
        return

    if not content:
        return

    # let BeautifulSoup sniff the encoding from meta tags automatically
    html = BeautifulSoup(content, "html.parser")

    title = _extract_title(html)
    if not title:
        return

    title = _clean_title(title)
    if len(title) > MAX_TITLE:
        title = title[:MAX_TITLE] + " ... [trunc]"

    return "^ \x02{}\x02".format(title)



# from __future__ import unicode_literals
# from util import hook, http
# from bs4 import BeautifulSoup

# import requests

# REGEX = r"(http|https)://(www.)?(?!(www.)?twitter|(www.)?youtube|bsky|youtu.be|(www.)?google|(en.)?wikipedia)[-a-zA-Z0-9@:%._\+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"

# MAX_TITLE = 100

# MAX_RECV = 1000000

# HEADERS = {
#     'Accept-Language': 'en-US,en;q=0.5',
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                   'Chrome/53.0.2785.116 Safari/537.36'
# }

# # @hook.regex(REGEX)
# # def titlesnarfer(match, say=None):
# #     try:
# #         page = http.get_html(match.group())
# #         #title = page.xpath("//title").text
# #         title = page.find(".//title").text
# #         #say("^ %s" % (title))
# #         return "^ %s" % (title)
# #     except:
# #         pass

# def get_encoding(soup):
#     meta_charset = soup.find('meta', charset=True)

#     if meta_charset:
#         return meta_charset['charset']

#     meta_content_type = soup.find(
#         'meta', {'http-equiv': lambda t: t and t.lower() == 'content-type', 'content': True}
#     )
#     if meta_content_type:
#         return requests.utils.get_encoding_from_headers({'content-type': meta_content_type['content']})

#     return None


# def parse_content(content, encoding=None):
#     html = BeautifulSoup(content, from_encoding=encoding)
#     old_encoding = encoding

#     encoding = get_encoding(html)

#     if encoding is not None and encoding != old_encoding:
#         html = BeautifulSoup(content, from_encoding=encoding)

#     return html


# @hook.regex(REGEX)
# def titlesnarfer(match):
#     try:
#         with requests.get(match.group(), headers=HEADERS, stream=True, timeout=3) as r:
#             if not r.encoding or not r.ok:
#                 return

#             content = r.raw.read(MAX_RECV, decode_content=True)
#             encoding = r.encoding
#     except requests.ReadTimeout:
#         # logger.debug("Read timeout reached for %r", match.group())
#         return

#     html = parse_content(content, encoding)

#     if html.title and html.title.text:
#         title = html.title.text.strip()

#         if len(title) > MAX_TITLE:
#             title = title[:MAX_TITLE] + " ... [trunc]"

#         out = "^ \x02{}\x02".format(title)
#         return out

