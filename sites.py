"""
Define CSS selectors for information extraction

In order to add a new site you have to go to that site and define CSS selectors
that point to the correct element. The easiest way to do this is to right click
the element and inspect it. If you don't know what I'm talking about read up on
CSS or X-Path selectors.

Note: I extended css selectors with a "*text" extractor to get the text inside
      of a parents children.

Example Site:
    'website_name': {
        # select result list
        'results': '',
        # select fields that contain info
        'fields': { 'name': '', 'area': '', 'rooms': '', 'rent': '', 'address': '', 'url': '' },
        # select next page button
        'next-page': ''
    },

"""

SELECTORS = {
    'immosuchmaschine.at': {
        'results': 'ul.result-list li.block_item',
        'fields': {
            'name': 'div.data_title h3 a::text',
            'area': 'div.data_size dd::text',
            'rooms': 'div.data_rooms dl::*text',
            'rent': 'div.data_price span::text',
            'address': 'span.data_zipcity_text::text',
            'url': 'div.data_title a::attr(href)'
        },
        'next-page': 'div.link.next::attr(data-href)'
    },
    'willhaben.at': {
        'results': 'div.result-list section.content-section',
        'fields': {
            'name': 'span[itemprop="name"]::text',
            'area': 'div.info span.desc-left::text',
            'rooms': 'div.info span.desc-left::text',
            'rent': 'div.info span.pull-right::text',
            'address': 'div.address-lg::text',
            'url': 'a[data-ad-link]::attr(href)'
        },
        'next-page': 'div.search-paging span.nav-icon:last-child a::attr(href)'
    },
    'flatbee.at': {
        'results': 'div#property_search_div div.property-boxv',
        'fields': {
            'name': 'h3.property-titlev a::text',
            'area': 'div.property-box-meta-itemv::*text',
            'rooms': 'div.property-box-meta-itemv::*text',
            'rent': 'table.sp_tbl td::text',
            'address': 'div.property-innerv h5.h_d_none::attr(innerHTML)',
            'url': 'h3.property-titlev a::attr(href)'
        },
        'next-page': 'ul.pagination li.next a::attr(href)'
    }
}

