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
        return soup

    def __first_login(self, username, is_inclu, pin):
        params = {
            'isInclu': is_inclu,
            'username': username,
            'pin': pin,
        }
        url = bpn_url.first_login
        header = bpn_header.login
        response = self.session.post(url, params=params, headers=header)
        self.soup = Soup(response.text, PARSER)

