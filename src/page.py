from bs4 import BeautifulSoup as Soup
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from util import lazy_property, make_url, make_regex_state
import requests

class Page(object):

    def __init__(self, session):
        self.session = session

