from bs4 import BeautifulSoup as Soup
import bpn_header
import re
import requests
import bpn_url

PARSER = 'html5lib'

class Bpn(object):

    def __init__(self, username, password, is_inclu=False, pin=''):
        self.username = username
        self.session = requests.Session()
        self.states = {}
        self.soup = None
        self.__login(username, password, is_inclu, pin)

    def __login(self, username, password, is_inclu, pin):
        soup = self.__first_login(username, is_inclu, pin)
        tag = soup.select_one('#LoginForm input[name="_STATE_"]')
        state = tag['value']
        self.__second_login(username, password, state)
        tag = soup.select_one('#RedirectHomeForm input[name="_STATE_"]')
        state = tag['value']
        self.__home(state)

    def __first_login(self, username, is_inclu, pin):
        params = {
            'isInclu': is_inclu,
            'username': username,
            'pin': pin,
        }
        url = bpn_url.first_login
        header = bpn_header.login
        response = self.session.post(url, params=params, headers=header)
        soup = Soup(response.text, PARSER)
        return soup

    def __second_login(self, username, password, state):
        params = {
            'username': username,
            'password': password,
            'jsonRequest': True,
            'sfaInfo': '',
            'pcCompartida': True,
            'inclu': False,
            'recordarUsuario': False,
            '_STATE_': state,
        }
        url = bpn_url.second_login
        header = bpn_header.dologin
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        return json
    
    def __home(self, state):
        params = {
            '_STATE_': state,
        }
        url = bpn_url.home
        header = bpn_header.home
        response = self.session.post(url, params=params, headers=header)
        soup = Soup(response.text, PARSER)
        self.soup = soup
    
    def logout(self):
        url = bpn_url.logout
        header = bpn_header.logout
        response = self.session.get(url, headers=header)
        json = response.json()
        return json

