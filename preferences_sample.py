from helper import commute_time, re_cap
from urllib.parse import urljoin
import re

# Store which homes the crawler already looked at to avoid duplicates
SEEN_PATH = '/path/to/file'

CREDENTIALS = {
    # Will be used to notify you about new offers (sends an email to itself)
    'mail': {
        'address': 'your@email.address',
        'pass':    'your_password',
        'server':  'your.mailserver.address'
    },
    # Used to calculate the time it takes to get to your point of interests
    # Note: only necessary if you'd like to calculate commute time
    'gmaps': {
        'key': 'YOUR_GOOGLE_MAPS_DISTANCE_API_KEY'
    }
}

# Websites to scrape
# Perform a search on one of these websites and then paste the url which shows the results
# into one of the lists below
# Note: These websites need selectors defined in 'sites.py'
URLS = {
    'immosuchmaschine.at': [
        # 'url1', 'url2'
    ],
    'willhaben.at': [
    ],
    'flatbee.at': [
    ]
}

# Time it takes with public transport to get to these places
COMMUTES = {
    'Place A': 'Times Square, New York City',
    'Place B': 'Rue La Fayette, Paris'
  # 'Place Name': 'Address Name'
}


# Define if offer is interesting or not
# If all criteria are met then you will be notified about the offer
# Note: will be checked in list order
#       checking commute time first might result in unnecessary Google Maps API calls
CRITERIA = [
    # lambda home: 100 < home.rent <= 900,
    # lambda home: all(s not in home.name.lower() for s in {'bad', 'balcony'}),
    # lambda home: 2 < home.rooms < 5,
    # lambda home: commute_time(home.address, COMMUTES['Place A']) < 25,
]


SITES_TO_SCRAPE = [
    'willhaben.at'
]


def make_field_transformers(base_url):
    """
    Make the transformers for every field in an offer e.g. name, price, address
    After every field was extracted each transformation pipeline will be applied
    and then the actual object will be created.

    How the transformation pipelines work:
        'area': [fun1, fun2] => fun2(fun1(area_string))

    Note: re_cap is a nice helper function extract strings with Regex

    :param base_url: the base url of the website being crawled
    :return: dict with all the fields names of Home NamedTuple
             Example:
             {
                'name': [first_function, second_function], # transformation pipeline
                'area': [filter_bad, as_int, lambda x: x*2],
                ...
             }

    """
    german_num = '\d{1,3}(?:\.\d{3})*(?:,\d+)?'
    area_re = re_cap('({num})\s*(?:m²|m2|m^2|m 2)'.format(num=german_num))
    rooms_re = re_cap('[Zz]immer\s*(\d+)', '(\d+)\s+[Zz]immer')
    price_re = re_cap('€?\s*({num})(?:,-|€)?'.format(num=german_num))
    address_re = re_cap('((?:\w.+,\s+)?\d\d\d\d \w+)', '(\w+ \d\d\.)')
    as_int = lambda s: int(re.sub(',\d*', '', s.replace('.', '')))

    return {
        'name':    [str.strip],
        'area':    [area_re, as_int],
        'rooms':   [rooms_re, as_int],
        'rent':    [price_re, as_int],
        'address': [address_re, lambda x: x.replace('\n', '')],
        'url':     [str.strip, lambda url: urljoin(base_url, url.replace('file://', '')).replace('http:', 'https:')]
    }

