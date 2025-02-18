from __future__ import unicode_literals
from util import hook, http


REGEX = r"(http|https)://(www.)?(?!(www.)?twitter|(www.)?youtube|bsky|youtu.be|(www.)?google|(en.)?wikipedia)[-a-zA-Z0-9@:%._\+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"

@hook.regex(REGEX)
def titlesnarfer(match, say=None):
    try:
        page = http.get_html(match.group())
        #title = page.xpath("//title").text
        title = page.find(".//title").text
        #say("^ %s" % (title))
        return "^ %s" % (title)
    except:
        pass
