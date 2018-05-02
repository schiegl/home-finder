import preferences
import re
from typing import Tuple
from urllib.parse import quote_plus
from functools import lru_cache
import urllib.request
import json


def re_cap(*regexes):
    """
    Capture first of the supplied regex
    :param regexes: list or regex strings
    :return: captured string | None
    """
    def go(string):
        for reg in regexes:
            matches = re.search(reg, string)
            if matches:
                return matches.group(1)
        return None
    return go


def pipe(funs, input):
    """
    Compose functions in pipe
    :param funs: functions
    :param input function input
    :return: function
    """
    for f in funs:
        if input:
            input = f(input)
        else:
            return None
    return input


@lru_cache(maxsize=None)
def commute_time(origin: str, dest: str) -> int:
    """
    How far are they apart?
    Caches queries to avoid unnecessary API calls
    :param origin: origin location
    :param dest:   destination location
    :exception:    if JSON response didn't find location or (KeyError,IndexError)
                   or network problem
    :return:       error message or commute in minutes
    """
    key = preferences.CREDENTIALS['gmaps']['key']
    origin_enc = quote_plus(origin)
    dest_enc = quote_plus(dest)
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'  + \
          'units=metric&origins={}&destinations={}'.format(origin_enc, dest_enc) + \
          '&mode=transit&key={}'.format(key)

    with urllib.request.urlopen(url) as req:
        data = json.loads(req.read().decode())

    # distance_m = data['rows'][0]['elements'][0]['commute_time']['value']
    duration_s = data['rows'][0]['elements'][0]['duration']['value']
    return int(round(duration_s / 60, 0))

