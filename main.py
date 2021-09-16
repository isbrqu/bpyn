import requests
from bs4 import BeautifulSoup as Soup
import header
import config

scheme = 'https'
domain = 'hb.redlink.com.ar'
directory = 'bpn'
base_url = f'{scheme}://{domain}/{directory}'

# login
url = f'{base_url}/doLoginFirstStep.htm'
params = {
    'isInclu': False,
    'username': config.username,
    'pin': '',
}
with requests.Session() as session:
    response = session.get(url, params=params, headers=header.login)
    soup = Soup(response.text, 'html5lib')
    # termina el login y adquiere la cookie LINKS
    state = soup.select_one('#LoginForm input[name="_STATE_"]')['value']
    print(state)

    # adquiere los state del home
    state = soup.select_one('#RedirectHomeForm input[name="_STATE_"]')['value']
    print(state)

