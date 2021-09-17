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
    # accede a posición consolidada y toma el state de getCuentasForPc
    url = f'{base_url}/posicionConsolidada.htm'
    params = {
        '_STATE_': state,
    }
    response = session.post(url, params=params, headers=header.position)
    soup = Soup(response.text, 'html5lib')
    regex = r"getCuentasForPC.htm\?_STATE_=(.+)'"
    pattern = re.compile(regex)
    state = pattern.search(soup.text).group(1)
    print(state)
    # obtiene las cuentas en un json
    try:
        url = f'{base_url}/getCuentasForPC.htm'
        params = {
            '_STATE_': state,
        }
        json = session.get(url, params=params, headers=header.accounts).json()
        accounts = json['response']['data']
        # obtengo el state de de posicionConsolidada para getSaldoPosCons
        url = f'{base_url}/getSaldoPosCons.htm'
        regex = r"getSaldoPosCons.htm\?_STATE_=(.+)'"
        pattern = re.compile(regex)
        state = pattern.search(soup.text).group(1)
        for account in accounts:
            params = {
                '_STATE_': state,
                'numero': account['numero'],
                'tipoTandem': account['tipoTandem'],
            }
            json = session.get(url, params=params, headers=header.balance).json()
            print(json)
    except Exception as exception:
        print(exception)
    finally:
        # cierra sesion
        url = f'{base_url}/logout.htm'
        response = session.get(url, headers=header.logout)
        print(response.text)

