from bpn_header import transferences as HEADERS
from functools import wraps
from requests.models import Response

SCHEME = 'https'
DOMAIN = 'hb.redlink.com.ar'
URL_DIRECTORY = 'bpn'
URL_BASE = f'{SCHEME}://{DOMAIN}/{URL_DIRECTORY}'

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

class Request(object):

    def __init__(self, method, path, headers=None):
        self.method = method.upper()
        self.path = path
        self.headers = headers or HEADERS

    def __call__(self, function):
        @wraps(function)
        def wrapper(obj):
            args = {}
            args['url'] = f'{URL_BASE}/{self.path}.htm'
            args['method'] = self.method
            args['headers'] = self.headers
            params = function(obj, self.path)
            if isinstance(params, dict):
                args['params'] = params
                response = obj.session.request(**args)
                return response
            return self.generator(params, obj, args)
        return wrapper

    def generator(self, params, obj, args):
        for param in params:
            args['params'] = param
            response = obj.session.request(**args)
            yield response

class GetRequest(Request):

    def __init__(self, path, *args, **kwargs):
        super().__init__('GET', path, *args, **kwargs)

class PostRequest(Request):

    def __init__(self, path, *args, **kwargs):
        super().__init__('POST', path, *args, **kwargs)

def json(function):
    @wraps(function)
    def wrapper(self):
        response = function(self)
        if isinstance(response, Response):
            json = response.json()
            return json
        generator = (subresponse.json() for subresponse in response)
        return generator
    return wrapper

SCRIPT = '//script[contains(. , $text)]/text()'

def state(name, css=None):
    def closure(function):
        @wraps(function)
        def wrapper(self, path):
            page = self.page(name)
            regex1 = fr'(?:{path}.+_STATE_=)'
            regex2 = r'([0-9A-F]+-[0-9A-F]+-[0-9A-F]+)'
            regexo = '?' if css else ''
            tag = page.css(css) if css else page.xpath(SCRIPT, text=path)
            state = tag.re_first(fr'{regex1}{regexo}{regex2}')
            params = function(self)
            if isinstance(params, dict):
                return add_state(params, state)
            generator = (add_state(param, state) for param in params)
            return generator
        return wrapper
    return closure

def add_state(params, state):
    params['_STATE_'] = state
    return params

