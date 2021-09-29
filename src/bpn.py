from bs4 import BeautifulSoup as Soup
import bpn_header
import re
import requests
import bpn_url
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

PARSER = 'html5lib'

def make_regex_state(string):
    return f'(?:"|\'){string}\.htm\?_STATE_=(.+)(?:"|\')'

def extract_state(obj, selector=None, attr=None, regex=None):
    if selector and attr:
        soup = Soup(obj, PARSER) if isinstance(obj, str) else obj
        tag = soup.select_one(selector)
        state = tag[attr]
        state = state.split('=')[1] if '=' in state else state
    elif regex:
        pattern = re.compile(regex)
        state = pattern.search(obj).group(1)
    else:
        raise Exception("selector, attr or regex isn't define")
    return state

def write_html(name, response):
    with open(f'{name}.html', 'w', encoding='utf-8') as html:
        html.write(response.text)

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
            self.response_home = response
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
        selector = '#_menu_movimientosHistoricos'
        state = realhref_state(self.soup_home, selector)
        print(state)
        url = bpn_url.movements
        params = {'_STATE_': state}
        header = bpn_header.movements
        response = self.session.post(url, params=params, headers=header)
        regex = r'/bpn/getCuentas\.htm\?_STATE_=(.+)(?:"|\')'
        pattern = re.compile(regex)
        state = pattern.search(response.text).group(1)
        print('state:', state)
        # write_html('foo', response)

    def last_movements(self):
        selector = '#_menu_ultimosMovimientos'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def movements_of_the_day(self):
        selector = '#_menu_movimientosDia'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def position(self):
        selector = '#_menu_posicionConsolidada'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def tendences(self):
        selector = '#_menu_posicion31DicWS'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def credin(self):
        selector = '#_menu_consultaCredin'
        state = realhref_state(self.soup_home, selector)
        # next
        params = {
            '_STATE_': state,
        }
        url = bpn_url.make('consultaCredin')
        header = bpn_header.transferences
        response = self.session.post(url, params=params, headers=header)
        section = 'showConsultaCredin'
        soup = Soup(response.text, PARSER)
        state = soup.select_one('#grilla')['source'].split('=')[1]
        params = {
            '_STATE_': state,
            'fechaDesde': '01/01/1999',
            'fechaHasta': '30/09/2021',
            'sentidoCredin': 'Enviados',
            'maxRows': 11,
            'page': 2,
        }
        url = bpn_url.make(section)
        header = bpn_header.balance
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        # json = json['response']['data']
        return json

    def cbu(self):
        selector = '#_menu_consultaCbu'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def buys(self):
        selector = '#_menu_consultasComprasComercios'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def creditcards(self):
        selector = '#_menu_consultaTarjetasCredito'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def documents(self):
        selector = '#_menu_gestionDocumentosElectronicosConsulta'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def balances(self):
        selector = '#_menu_saldos'
        state = realhref_state(self.soup_home, selector)
        print(state)

    def phone_recharge(self):
        section = 'consultaCargaValorTP'
        selector = f'//*[@id="_menu_{section}"]/@realhref'
        attr = 'realhref'
        # print(self.response_home.text)
        state = Selector(text=self.response_home.text).xpath(selector).get()
        state = state.split('=')[1]
        # state = extract_state(self.soup_home, selector=selector, attr=attr)
        # next
        params = {
            '_STATE_': state,
        }
        url = bpn_url.make(section)
        header = bpn_header.transferences
        response = self.session.post(url, params=params, headers=header)
        section = 'getRecargasConsultaCargaValor'
        selector = '#consultacargavalorForm input[name="_STATE_"]'
        attr = 'value'
        state = extract_state(response.text, selector=selector, attr=attr)
        data = {
            '_STATE_': state,
            'codigoEmpresa': '',
            'usuario': '',
            'canal': '',
            'importe': '',
            'perteneceA': '',
            'fechaDesde': '01/01/1999',
            'fechaHasta': '27/09/2021',
            'pageNumber': 1,
            'linesPerPage': 5,
            'codigoRubro': 'TP',
        }
        url = bpn_url.make(section)
        header = bpn_header.balance
        response = self.session.post(url, data=data, headers=header)
        json = response.json()
        # json = json['response']['data']
        return json

    def transferences(self):
        section = 'resumenTransferencias'
        selector = f'#_menu_{section}'
        attr = 'realhref'
        state = extract_state(self.soup_home, selector=selector, attr=attr)
        params = {
            '_STATE_': state,
        }
        url = bpn_url.make('resumenTransferencias')
        header = bpn_header.transferences
        response = self.session.post(url, params=params, headers=header)
        # json
        section =  'transferenciasByFilter'
        regex = make_regex_state(section)
        state = extract_state(response.text, regex=regex)
        params = {
            '_STATE_': state,
            'fechaDesde': '01/01/1999',
            'fechaHasta': '30/12/2021',
            'linesPerPage': 100,
            'pageNumber': 1,
            'orderingField': 'fechaMovimiento',
            'sortOrder': 'desc',
        }
        url = bpn_url.make(section)
        header = bpn_header.balance
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        # json = json['response']['data']
        return json

    def payments_made(self):
        section = 'pagosRealizados'
        selector = f'#_menu_{section}'
        attr = 'realhref'
        state = extract_state(self.soup_home, selector=selector, attr=attr)
        params = {
            '_STATE_': state,
        }
        url = bpn_url.make(section)
        header = bpn_header.transferences
        response = self.session.post(url, params=params, headers=header)
        # json
        json = self.__entity(response)
        item = json['response']['data'][0]['adheridos'][0]
        print(item)
        json = self.__payments_made(response, params_extra={
            'codAbre': item['codigoAbre'],
            'ente': item['codigoEnte'],
        })
        # json
        # json = json['response']['data']
        return json

    def __entity(self, response):
        section =  'obtenerLinkPagosEnte'
        regex = make_regex_state(section)
        state = extract_state(response.text, regex=regex)
        params = {
            '_STATE_': state,
        }
        url = bpn_url.make(section)
        header = bpn_header.balance
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        return json

    def __payments_made(self, response, params_extra={}):
        section = 'getPagosRealizados'
        selector = '#consultaPagosRealizadosForm input[name="_STATE_"]'
        attr = 'value'
        state = extract_state(response.text, selector=selector, attr=attr)
        params = {
            '_STATE_': state,
            'linkPagosEnte': '',
            'pagSgte': '',
            'pagAnt': '',
            'pagAct': 0,
            'fechaDesde': '28/09/1991',
            'fechaHasta': '28/09/2021',
            'importeDesde': '',
            'importeHasta': '',
            'vencDesde': '28/09/2021',
            'vencHasta': '',
        }
        params.update(params_extra)
        url = bpn_url.make(section)
        header = bpn_header.balance
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        return json

    def accounts_transferences(self):
        pass

    def logout(self):
        url = bpn_url.logout
        header = bpn_header.logout
        response = self.session.get(url, headers=header)
        json = response.json()
        return json

