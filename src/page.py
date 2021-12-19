from bs4 import BeautifulSoup as Soup
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from util import lazy_property, make_url, make_regex_state
import bpn_header
import requests

class Page(object):

    def __init__(self, bpn):
        self.bpn = bpn

    @lazy_property
    def login(self):
        # first login
        section = 'doLoginFirstStep'
        url = make_url(section)
        headers = bpn_header.login
        response = self.bpn.session.post(url, headers=headers, params={
            # 'isInclu': False,
            'username': self.bpn.username,
            # 'pin': '23123',
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @lazy_property
    def home(self):
        # entry to home
        page = self.login
        section = 'home'
        selector = '#RedirectHomeForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.home
        response = self.bpn.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page
