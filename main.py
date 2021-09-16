import requests
from bs4 import BeautifulSoup as Soup
from header import header
import config

scheme = 'https'
domain = 'hb.redlink.com.ar'
directory = 'bpn'
base_url = f'{scheme}://{domain}/{directory}'
login_url = f'{base_url}/doLoginFirstStep.htm'
params = {
    'isInclu': False,
    'username': config.username,
    'pin': '',
}

response = requests.get(login_url, params=params, headers=header)
soup = Soup(response.text, 'html5lib')

state_login = soup.select_one('#LoginForm input[name="_STATE_"]')['value']
state_home = soup.select_one('#RedirectHomeForm input[name="_STATE_"]')['value']

print(state_login)
print(state_home)

# with open('login.html', 'w', encoding='utf-8') as html:
#     html.write(soup.prettify())

