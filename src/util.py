from functools import wraps
import requests
from bpn_header import transferences as HEADERS

PARSER = 'html5lib'
SCHEME = 'https'
DOMAIN = 'hb.redlink.com.ar'
URL_DIRECTORY = 'bpn'
URL_BASE = f'{SCHEME}://{DOMAIN}/{URL_DIRECTORY}'

XPATH_SCRIPT = '//script[contains(. , $text)]/text()'
# REGEX_STATE = 

def make_url(name):
    return f'{URL_BASE}/{name}.htm'

def make_regex_state(name):
    return f'{name}\.htm.+=(.+)(:?"|\');'

# def homepage(fn, section):
#     def wrapper(self):
#         page = self.home
#         return fn(self, page)
#     return wrapper

def lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

# https://stackoverflow.com/a/60309236
class Request(object):

    def __init__(self, method='post', section, page):
        self.method = method.upper()
        self.section = section
        self.headers = HEADERS
        self.page = page

    def __call__(self, function):
        def wrapper(obj, *args, **kwargs):
            params = function(*args, **kwargs)
            args = {}
            args['url'] = make_url(section)
            args['method'] = self.method,
            args['headers'] = self.headers
            if params:
                args['params'] = params
            regex = make_regex_state(section)
            state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
            params['_STATE_'] = state
            return requests.request(**args)
        return wrapper
