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
        self.state = {}
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
        try:
            params = {
                '_STATE_': state,
            }
            url = bpn_url.home
            header = bpn_header.home
            response = self.session.post(url, params=params, headers=header)
            self.soup_home = Soup(response.text, PARSER)
            self.__states()
        except Exception as exception:
            print(exception)
        finally:
            # self.logout()
            pass

    def __states(self):
        regex = r'(\w+).htm\?_STATE_=(.+)(?:"|\')'
        pattern = re.compile(regex)
        self.states = dict(pattern.findall(self.soup_home.text))
    
    def movements(self):
        tag = self.soup_home.select_one('#_menu_movimientosHistoricos')
        state = tag['realhref'].split('=')[1]
        print(state)

    def last_movements(self):
        selector = '#_menu_ultimosMovimientos'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def movements_of_the_day(self):
        selector = '#_menu_movimientosDia'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def position(self):
        tag = self.soup_home.select_one('#_menu_posicionConsolidada')
        state = tag['realhref'].split('=')[1]
        print(state)

    def tendences(self):
        selector = '#_menu_posicion31DicWS'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def debin(self):
        selector = '#_menu_consultaCredin'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def cbu(self):
        tag = self.soup_home.select_one('#_menu_consultaCbu')
        state = tag['realhref'].split('=')[1]
        print(state)

    def buys(self):
        selector = '#_menu_consultasComprasComercios'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def creditcards(self):
        selector = '#_menu_consultaTarjetasCredito'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def documents(self):
        selector = '#_menu_gestionDocumentosElectronicosConsulta'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def balances(self):
        selector = '#_menu_saldos'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def phone_recharge(self):
        selector = '#_menu_consultaCargaValorTP'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def transferences(self):
        selector = '#_menu_resumenTransferencias'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def payments_made(self):
        selector = '#_menu_pagosRealizados'
        tag = self.soup_home.select_one(selector)
        state = tag['realhref'].split('=')[1]
        print(state)

    def balance(self):
        params = {
            '_STATE_': self.states['posicionConsolidada'],
        }
        url = bpn_url.position
        header = bpn_header.position
        response = self.session.post(url, params=params, headers=header)
        soup = Soup(response.text, PARSER)
        regex = r"getCuentasForPC.htm\?_STATE_=(.+)'"
        pattern = re.compile(regex)
        state = pattern.search(soup.text).group(1)
        params = {
            '_STATE_': state,
        }
        url = bpn_url.accounts
        header = bpn_header.accounts
        response = self.session.get(url, params=params, headers=header)
        json = response.json()
        accounts = json['response']['data']
        # obtengo el state de de posicionConsolidada para getSaldoPosCons
        url = bpn_url.balance
        header = bpn_header.balance
        regex = r"getSaldoPosCons.htm\?_STATE_=(.+)'"
        pattern = re.compile(regex)
        state = pattern.search(soup.text).group(1)
        for account in accounts:
            params = {
                '_STATE_': state,
                'numero': account['numero'],
                'tipoTandem': account['tipoTandem'],
            }
            response = self.session.get(url, params=params, headers=header)
            json = response.json()
            yield json
    
    def logout(self):
        url = bpn_url.logout
        header = bpn_header.logout
        response = self.session.get(url, headers=header)
        json = response.json()
        return json

