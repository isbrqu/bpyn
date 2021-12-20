from functools import wraps

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
