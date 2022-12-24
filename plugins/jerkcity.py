from random import randrange

from util import http, hook


@hook.command('bonequest')
@hook.command
def jerkcity(inp, say=None):
    max_response = http.get_json('https://www.bonequest.com/api/v2/')
    max_episode = max_response['episodes'][0]['episode']
    rand_episode = randrange(1, int(max_episode))
    rand_response = http.get_json('https://www.bonequest.com/api/v2/episodes/{}'.format(rand_episode))
    episode = rand_response['episodes'][0]
    reply = ('\x02Title\x02: {} | \x02Episode\x02: {} | https://www.bonequest.com/{}.gif | \x02Date\x02: {}-{}-{}'
            .format(episode['title'],  
                    episode['episode'],
                    episode['episode'],
                    episode['month'],
                    episode['day'],
                    episode['year']
            )
    )
    say(reply)
