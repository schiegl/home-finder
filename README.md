# Home Finder

Automatically search home-search-engines and get an E-Mail notification if an ad fits your preferences. This can mean things such as 2-4 rooms, > 50m² or commute to work in fewer than 20 minutes.

## Usage

### 1. Dependencies
Install all the necessary dependencies
* Firefox
* [geckodriver](https://github.com/mozilla/geckodriver/releases) (needs to be in your PATH otherwise it won't find it!)
* Python 3 + selenium
* Google Maps Distance API key (optional)
* E-Mail account

### 2. Write preferences
Rename `preferences_sample.py` to `preferences.py` and fill in the necessary information.

### 3. Add site (optional)
Every ad for a home is captured as a `Home` object and in order to fill the fields in `Home` every site needs CSS selectors defined to extract information out of the webpage. If you're unfamiliar with CSS selectors take a look at this [cheat sheet/tutorial](https://www.w3schools.com/cssref/css_selectors.asp).

The selectors are defined in `sites.py`.

```python
class Home(NamedTuple):
    """
    Store information about a home
    """
    name: str
    area: int
    rooms: int
    rent: int
    address: str
    url: str

# Example selector
{
    'sitename': {
        'results': 'div.result-list section.content-section',
        'fields': {
            'name':    'span[itemprop="name"]::text',
            'area':    'div.info span.desc-left::text',
            'rooms':   'div.info span.desc-left::text',
            'rent':    'div.info span.pull-right::text',
            'address': 'div.address-lg::text',
            'url':     'a[data-ad-link]::attr(href)'
        },
        'next-page': 'div.search-paging span.nav-icon:last-child a::attr(href)'
    }
}
```

### 4. Run the program

```shell
python3 homefinder.py
```

### 5. Automate this program (optional)
I suggest either running this program with cronjob on your server or just on startup of your personal computer.

## Notes
I tried to make this as plug-n-play as possible but you probably still need to learn how to use CSS selectors and install geckodriver.

