"""Weather, thanks to pirateweather and google geocoding."""
from __future__ import unicode_literals

from util import hook, http

from datetime import datetime, timedelta
import pytz
import pendulum


GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
PIRATEWEATHER_URL = "https://api.pirateweather.net/forecast/"


def geocode_location(api_key, loc):
    """Get a geocoded location from gooogle's geocoding api."""
    try:
        parsed_json = http.get_json(GEOCODING_URL, address=loc, key=api_key)
    except IOError:
        return None

    return parsed_json


def get_weather_data(api_key, lat, long):
    """Get weather data from pirateweather."""
    query = "{key}/{lat},{long}".format(key=api_key, lat=lat, long=long)
    url = PIRATEWEATHER_URL + query
    try:
        parsed_json = http.get_json(url)
    except IOError:
        return None

    return parsed_json


def f_to_c(temp_f):
    """Convert F to C."""
    return (temp_f - 32) * 5 / 9


def mph_to_kph(mph):
    """Convert mph to kph."""
    return mph * 1.609

def mph_to_mps(mph):
    """Convert kph to mps."""
    return mph * 0.44704


def next_unix_times(timezone_str):
    # Define the times to check
    target_times = [(6, 0), (14, 0), (22, 0)]  # (hour, minute) for 6am, 2pm, 10pm
    now = datetime.now(pytz.timezone(timezone_str))
    
    next_times = []
    for hour, minute in target_times:
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if target_time <= now:
            target_time += timedelta(days=1)
        
        next_times.append(target_time)
    
    # Sort and take the next 3 occurrences
    next_times.sort()
    
    # Convert to Unix timestamps
    unix_times = [int(t.timestamp()) for t in next_times]
    
    return unix_times

def make_dayname(utcts, tzoffset):
    """convert offset datetime to something readable"""
    ts = utcts + tzoffset * 3600

    if pendulum:
        dt = pendulum.from_timestamp(ts)
        return dt.format('dddd hA')
    return ts

def format_forecast(u_time, conditions, temp, tzoffset):
    """format forecast for output"""
    f_time = make_dayname(u_time, tzoffset)
    # f_temp = format_temp(temp)
    f_temp = "{}F/{}C".format(round(temp), round(f_to_c(temp)))
    
    f_forecast = "| \x02{}\x02 :: \x02{}\x02 : {} ".format(f_time, conditions, f_temp)
    return f_forecast 

@hook.api_key("google", "pirateweather")
@hook.command("w",autohelp=False)
@hook.command(autohelp=False)
def weather(inp, chan="", nick="", reply=None, db=None, api_key=None):
    """.weather <location> [dontsave] | @<nick> -- Get weather data."""
    if "google" not in api_key and "pirateweather" not in api_key:
        return None

    # this database is used by other plugins interested in user's locations,
    # like .near in tag.py
    db.execute(
        "create table if not exists "
        "location(chan, nick, loc, lat, lon, primary key(chan, nick))"
    )

    if inp[0:1] == "@":
        nick = inp[1:].strip()
        loc = None
        dontsave = True
    else:
        dontsave = inp.endswith(" dontsave")
        # strip off the " dontsave" text if it exists and set it back to `inp`
        # so we don't report it back to the user incorrectly
        if dontsave:
            inp = inp[:-9].strip().lower()
        loc = inp

    if not loc:  # blank line
        loc = db.execute(
            "select loc, lat, lon from location where chan=? and nick=lower(?)",
            (chan, nick),
        ).fetchone()
        if not loc:
            return weather.__doc__
        addr, lat, lng = loc
    else:
        location = geocode_location(api_key["google"], loc)

        if not location or location.get("status") != "OK":
            reply("Failed to determine location for {}".format(inp))
            return

        geo = location.get("results", [{}])[0].get("geometry", {}).get("location", None)
        if not geo or "lat" not in geo or "lng" not in geo:
            reply("Failed to determine location for {}".format(inp))
            return

        addr = location["results"][0]["formatted_address"]
        lat = geo["lat"]
        lng = geo["lng"]

    parsed_json = get_weather_data(api_key["pirateweather"], lat, lng)
    current = parsed_json.get("currently")

    if not current:
        reply("Failed to get weather data for {}".format(inp))
        return

    forecast = parsed_json["daily"]["data"][0]
    hourly_forecast = parsed_json["hourly"]["data"]

    # Get the next 3 times to check
    next_times = next_unix_times(parsed_json['timezone'])


    # Filter hourly forecast for the next 3 times
    filtered_forecast = [hour for hour in hourly_forecast if hour['time'] in next_times]

    forecast_str = ""
    for hour in filtered_forecast:
        forecast_str += format_forecast(hour['time'], hour['summary'], hour['temperature'], parsed_json['offset'])

    info = {
        "city": addr,
        "t_f": current["temperature"],
        "t_c": f_to_c(current["temperature"]),
        "h_f": forecast["temperatureHigh"],
        "h_c": f_to_c(forecast["temperatureHigh"]),
        "l_f": forecast["temperatureLow"],
        "l_c": f_to_c(forecast["temperatureLow"]),
        "feels_like_f": current["apparentTemperature"],
        "feels_like_c": f_to_c(current["apparentTemperature"]),
        "weather": current["summary"],
        "humid": int(current["humidity"] * 100),
        "wind": "Wind: {mph:.1f}mph/{kph:.1f}kph/{mps:.1f}mps".format(mph=current["windSpeed"], kph=mph_to_kph(current["windSpeed"]), mps=mph_to_mps(current["windSpeed"])),
        "forecast": parsed_json.get("hourly", {}).get("summary", ""),
    }

    reply("(\x02{city}\x02) :: \x02{weather}\x02 | " \
        "\x02Temp\x02: {t_f:.1f}F/{t_c:.1f}C | " \
        "\x02Feels Like\x02: {feels_like_f:.1f}F/{feels_like_c:.1f}C | " \
        "\x02Humidity\x02: {humid}% | " \
        "{wind} ".format(**info)  + forecast_str)


    if inp and not dontsave:
        db.execute(
            "insert or replace into "
            "location(chan, nick, loc, lat, lon) "
            "values (?, ?, ?, ?, ?)",
            (chan, nick.lower(), addr, lat, lng),
        )
        db.commit()
