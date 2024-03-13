from util import http, hook

@hook.command(autohelp=False)
def fml(inp):
    try:
        r = http.get_json('https://q.beanteam.org/api/fml/random')
        return "{} | \x02Agreed\x02: {} - \x02Deserved\x02: {}".format(r["text"], r["your_life_sucks"], r["you_deserved_it"])
    except:
        pass

@hook.command(autohelp=False)
def marx(inp, say=None):
    try:
        response = http.get_json('https://q.beanteam.org/api/marx/random')
        #say("{} | \x02Source\x02: {} \x02Year\x02: {}".format(response['quote'], response['source'], response['year']))
        full_text = "{} | \x02Source\x02: {} - \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
        text_list = split_text(full_text)
        for block in text_list:
            say(block)
            return
    except:
        pass

@hook.command(autohelp=False)
def trotsky(inp, say=None):
    try:
        response = http.get_json('https://q.beanteam.org/api/trotsky/random')
        # say("{} | \x02Source\x02: {} \x02Year\x02: {}".format(response['quote'], response['source'], response['year']))
        full_text = "{} | \x02Source\x02: {} - \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
        text_list = split_text(full_text)
        for block in text_list:
            say(block)
        return
    except:
        pass

@hook.command(autohelp=False)
def engels(inp, say=None):
    try:
        response = http.get_json('https://q.beanteam.org/api/engels/random')
        full_text = "{} | \x02Source\x02: {} - \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
        text_list = split_text(full_text)
        for block in text_list:
            say(block)        
        return
    except:
        pass


def split_text(text, max_length=500):
    words = text.split()
    result = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + len(current_chunk.split()) <= max_length:
            current_chunk += " " + word if current_chunk else word
        else:
            result.append(current_chunk.strip())
            current_chunk = word

    if current_chunk:
        result.append(current_chunk.strip())

    return result