import requests
from bs4 import BeautifulSoup as Soup
import header
import config
import re

scheme = 'https'
domain = 'hb.redlink.com.ar'
directory = 'bpn'
base_url = f'{scheme}://{domain}/{directory}'

# login
with requests.Session() as session:
    # realiza la primera instancia de login
    url = f'{base_url}/doLoginFirstStep.htm'
    params = {
        'isInclu': False,
        'username': config.username,
        'pin': '',
    }
    response = session.get(url, params=params, headers=header.login)
    soup = Soup(response.text, 'html5lib')

    # termina el login y adquiere la cookie LINKS
    url = f'{base_url}/doLogin.htm'
    state = soup.select_one('#LoginForm input[name="_STATE_"]')['value']
    params = {
        'username': config.username,
        'password': config.password,
        'jsonRequest': True,
        'sfaInfo': '',
        'pcCompartida': True,
        'inclu': False,
        'recordarUsuario': False,
        '_STATE_': state,
    }
    response = session.post(url, params=params, headers=header.dologin)
    print(response.text)

    # adquiere los state del home
    url = f'{base_url}/home.htm'
    state = soup.select_one('#RedirectHomeForm input[name="_STATE_"]')['value']
    params = {
        '_STATE_': state,
    }
    response = session.post(url, params=params, headers=header.home)
    soup = Soup(response.text, 'html5lib')
    # obtiene el state de posicion consolidada
    regex = r'posicionConsolidada.htm\?_STATE_=(.+)"'
    pattern = re.compile(regex)
    state = pattern.search(soup.text).group(1)
    print(state)
    print(response.text)

