from io import StringIO
from typing import NamedTuple, List, Set, Tuple, Optional
from sites import SELECTORS
from preferences import URLS
from selenium.webdriver import FirefoxProfile, FirefoxOptions, Firefox
from selenium.common.exceptions import NoSuchElementException
from notification import notify_about_home, notify_dev
import re
from helper import pipe
import time
import logging as log
from preferences import SEEN_PATH, CRITERIA, make_field_transformers, SITES_TO_SCRAPE
from hashlib import md5
from contextlib import contextmanager
import sys


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


def fingerprint(home: Home):
    """
    Get 'unique' id for home Object
    :param home: defined Home object
    :return: md5 string
    """
    return md5('{}{}{}{}{}{}'.format(home.name, home.area, home.rooms,
                                     home.rent, home.address, home.url)
               .encode('utf-8')).hexdigest()


def show(name):
    """
    Print out something in a pipeline without affecting the input
    """
    def go(x):
        print(name, '->', x)
        return x
    return go


class HomeSpider:
    """
    Crawl home-search-engine websites
    """
    def __init__(self, selectors, domain_name):
        self.selectors = selectors
        self.base_url = 'https://www.' + domain_name
        self.required = {'name', 'area', 'rooms', 'rent', 'address', 'url'}
        self.transformers = make_field_transformers(self.base_url)

    def __enter__(self):
        options = FirefoxOptions()
        options.set_headless(True)
        profile = FirefoxProfile()
        self.browser = Firefox(firefox_options=options, firefox_profile=profile)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            log.error(exc_type, exc_value, traceback)
        self.browser.quit()

    def parse_page(self, page_results):
        """
        Parse a home website
        :param page_results: list of page results
        :return: list of correctly parsed homes
        """
        for result in page_results:
            fields = {}
            errors = []
            try:
                for name, sel in self.selectors['fields'].items():
                    raw = self.extract(sel, result)
                    if raw is None:
                        errors.append('Failed to extract field "{}"'.format(name))
                    else:
                        val = pipe(self.transformers[name], raw)
                        if val is None:
                            errors.append('Failed to transform field "{}" with input "{}"'.format(name, val))
                        else:
                            fields[name] = val

            except Exception as e:
                errors.append('{}, {}'.format(type(e), e.args[0]))
            finally:
                if not errors:
                    yield Home(**fields)
                else:
                    fields, missing = self.fill_in_blank(fields)
                    if missing:
                        self.handle_parse_error(errors, result)
                    else:
                        yield Home(**fields)

    @contextmanager
    def get_and_wait(self, url, timeout=10):
        """
        Get webpage and wait for it to load
        :param url: a url string
        :param timeout: timeout in seconds
        :return: None
        """
        old_page = self.browser.page_source
        self.browser.get(url)
        for i in range(0, timeout):
            time.sleep(1)
            if self.browser.page_source != old_page:
                break

        if self.browser.page_source != old_page:
            yield
        else:
            log.error('Page Timeout', url)

    def crawl_next_page(self, next_url: Optional[str]) -> Tuple[List[Home], Optional[str]]:
        """
        Crawl all urls
        :return: List of selfs
        """
        if next_url:
            with self.get_and_wait(next_url):
                homes = list(self.parse_page(self.extract(self.selectors['results'])))
                next_url = self.extract(self.selectors['next-page'])
                return homes, next_url
        else:
            return [], None

    def extract(self, selector: str, web_el=None):
        """
        Extract text or attribute content from html elements
        :param selector: css selector
        :param web_el: root html element or if none then the entire document is used
        :return: content string or list of content strings
        """
        try:
            if not web_el:
                web_el = self.browser.find_element_by_tag_name('html')

            if '::' not in selector:
                return self.browser.find_elements_by_css_selector(selector)
            else:
                sub_sel, ext = selector.split('::')
                if ext == 'text':
                    return web_el.find_element_by_css_selector(sub_sel).text
                elif ext == '*text':
                    el_sel = web_el.find_elements_by_css_selector(sub_sel)
                    fragments = filter(lambda x: x != '', map(lambda x: x.text.replace('\n',' ').strip(), el_sel))
                    return ' ** '.join(fragments)
                else:
                    attr = re.search('attr\((.+)\)', ext)
                    if attr:
                        return web_el.find_element_by_css_selector(sub_sel).get_attribute(attr.group(1))

        except NoSuchElementException:
            return None

    def fill_in_blank(self, fields):
        """
        Fill in fields 'intelligently'
        :param fields:
        :return: filled in fields, missing fields
        """
        _fields = fields.copy()
        missing = self.required - _fields.keys()
        # probably just a room for rent and not whole apartment
        if 'rooms' in missing and 'area' in fields and fields['area'] < 70:
            _fields['rooms'] = 1
        if 'area' in missing and 'rooms' in fields and fields['rooms'] == 1:
            _fields['area'] = 30
        missing = self.required - _fields.keys()
        return _fields, missing

    def handle_parse_error(self, errors, web_element):
        """
        Log errors
        :param errors: list of error descriptions
        :param web_element: html element where error happened
        """
        msg = '= PARSE ERROR =====\n' \
              'Site: {site}\n' \
              'Errors:\n\t - {errs}\n' \
              '---- HTML ----\n' \
              '{html}\n' \
              '---- HTML END ----'.format(
                site=self.base_url, errs='\n\t - '.join(errors),
                html=web_element.get_attribute('innerHTML')
              )

        log.error(msg + '\n')


def crawl_website(name: str, seen: Set[str], depth=9999):
    log.info('Going to ' + name)
    new_homes = set()

    with HomeSpider(SELECTORS[name], name) as spider:
        for next_url in URLS[name]:
            i = 1
            while i <= depth and next_url:
                log.info('{}/{} {}'.format(i, depth, next_url))
                i += 1
                homes, next_url = spider.crawl_next_page(next_url)

                dups_in_row = 0
                for home in homes:
                    if fingerprint(home) in seen or home in new_homes:
                        dups_in_row += 1
                        if dups_in_row >= 3:
                            log.info('Now new homes...')
                            next_url = None
                            break
                    else:
                        dups_in_row = 0
                        new_homes.add(home)

    return new_homes


def main():
    """
    Run crawler
    """
    logger = log.getLogger()
    logger.setLevel(log.INFO)
    logger.addHandler(log.StreamHandler(sys.stdout))
    debugio = StringIO()
    logger.addHandler(log.StreamHandler(debugio))

    with open(SEEN_PATH, 'r') as f:
        seen = set(f.read().splitlines()) # mutable!
        old_seen = seen.copy()

    for name in SITES_TO_SCRAPE:
        new_homes = crawl_website(name, seen)
        seen = seen.union(map(fingerprint, new_homes))
        log.info('Found {} new homes'.format(len(new_homes)))
        for home in new_homes:
            if all(must(home) for must in CRITERIA):
                notify_about_home(home)

    with open(SEEN_PATH, 'a') as f:
        f.writelines(h + '\n' for h in (seen - old_seen))

    logs = debugio.getvalue()
    if 'error' in logs.lower():
        log.info('Informing developer about errors')
        notify_dev('Crawling Errors', logs)

    log.info('Bye!')


if __name__ == '__main__':
    main()


