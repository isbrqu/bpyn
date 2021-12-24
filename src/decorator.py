from bpn_header import transferences as HEADERS

SCHEME = 'https'
DOMAIN = 'hb.redlink.com.ar'
URL_DIRECTORY = 'bpn'
URL_BASE = f'{SCHEME}://{DOMAIN}/{URL_DIRECTORY}'

# https://stackoverflow.com/a/60309236
class Request(object):

    def __init__(self, method, path, headers=None):
        self.method = method.upper()
        self.path = path
        self.headers = headers or HEADERS

    def __call__(self, function):
        def wrapper(obj):
            args = {}
            args['url'] = f'{URL_BASE}/{self.path}.htm'
            args['method'] = self.method
            args['headers'] = self.headers
            args['params'] = function(obj, self.path)
            response = obj.session.request(**args)
            return response
        return wrapper

class GetRequest(Request):

    def __init__(self, path, *args, **kwargs):
        super().__init__('GET', path, *args, **kwargs)

class PostRequest(Request):

    def __init__(self, path, *args, **kwargs):
        super().__init__('POST', path, *args, **kwargs)

def json(function):
    def wrapper(*args, **kwargs):
        response = function(*args, **kwargs)
        json = response.json()
        return json
    return wrapper

