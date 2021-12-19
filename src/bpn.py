from bs4 import BeautifulSoup as Soup
import bpn_header
import re
import requests
from scrapy.selector import Selector
from pprint import pprint
from scrapy.http import HtmlResponse
from functools import wraps

PARSER = 'html5lib'
SCHEME = 'https'
DOMAIN = 'hb.redlink.com.ar'
URL_DIRECTORY = 'bpn'
URL_BASE = f'{SCHEME}://{DOMAIN}/{URL_DIRECTORY}'

XPATH_SCRIPT = '//script[contains(. , $text)]/text()'
# REGEX_STATE = 

def make_url(name):
    return f'{URL_BASE}/{name}.htm'

def make_regex_state(name):
    return f'{name}\.htm.+=(.+)(:?"|\');'

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

class Bpn(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.cookies.set('cookieTest', 'true')
        self.__login(username, password)

    @lazy_property
    def login_page(self):
        # first login
        section = 'doLoginFirstStep'
        url = make_url(section)
        headers = bpn_header.login
        response = self.session.post(url, headers=headers, params={
            # 'isInclu': False,
            'username': self.username,
            # 'pin': '23123',
        })
        page = HtmlResponse(url, body=response.content)
        return page

    def __login(self, username, password):
        page = self.login_page
        # second login, get LINKS cookie
        section = 'doLogin'
        selector = '#LoginForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.login
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
            'username': username,
            'password': password,
            'jsonRequest': True,
            'sfaInfo': '',
            'pcCompartida': False,
            'inclu': False,
            'recordarUsuario': False,
        })

    @lazy_property
    def home_page(self):
        # entry to home
        page = self.login_page
        section = 'home'
        selector = '#RedirectHomeForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.home
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @lazy_property
    def balance_page(self):
        page = self.home_page
        section = 'saldos'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @lazy_property
    def credin_page(self):
        page = self.home_page
        section = 'consultaCredin'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @property
    def credin(self):
        page = self.credin_page
        section = 'showConsultaCredin'
        selector = '#grilla'
        state = page.css(selector).xpath('@source').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
            'fechaDesde': '01/01/1999',
            'fechaHasta': '30/09/2021',
            'sentidoCredin': 'Enviados',
            'maxRows': 11,
            'page': 2,
        })
        json = response.json()
        return json

    def movements(self):
        selector = '#_menu_movimientosHistoricos'
        state = realhref_state(self.soup_home, selector)
        print(state)
        url = make_url('movimientosHistoricos')
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

    @lazy_property
    def accounts(self):
        # get accounts
        page = self.balance_page
        section = 'getCuentas'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json

    @property
    def balances(self):
        page = self.balance_page
        json = self.accounts
        # get balances
        section = 'getSaldo'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.balance
        for account in json['response']['data']:
            response = self.session.post(url, headers=headers, params={
                '_STATE_': state,
                'numero': account['numero'],
                'tipoTandem': account['tipoTandem']
            })
            yield response.json()

    @property
    def total_balance(self):
        # required to calculate the total balance
        [_ for _ in self.balances]
        # normal query
        page = self.balance_page
        section = 'getSaldosTotales'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json

    @property
    def phone_recharge(self):
        # first request
        page = self.home_page
        section = 'consultaCargaValorTP'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        # get values
        section = 'getRecargasConsultaCargaValor'
        selector = '#consultacargavalorForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
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
        })
        json = response.json()
        return json

    @property
    def transferences(self):
        page = self.home_page
        section = 'resumenTransferencias'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        # get values
        section =  'transferenciasByFilter'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
            'fechaDesde': '01/01/1999',
            'fechaHasta': '30/12/2021',
            'linesPerPage': 100,
            'pageNumber': 1,
            'orderingField': 'fechaMovimiento',
            'sortOrder': 'desc',
        })
        json = response.json()
        return json

    @lazy_property
    def payments_page(self):
        page = self.home_page
        section = 'pagosRealizados'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @lazy_property
    def entities(self):
        # get entities
        page = self.payments_page
        section =  'obtenerLinkPagosEnte'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.balance
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json

    @property
    def payments_made(self):
        # get values
        page = self.payments_page
        json = self.entities
        section = 'getPagosRealizados'
        selector = '#consultaPagosRealizadosForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.balance
        for entity in json['response']['data'][0]['adheridos']:
            response = self.session.post(url, headers=headers, params={
                '_STATE_': state,
                'codAbre': entity['codigoAbre'],
                'ente': entity['codigoEnte'],
                # 'linkPagosEnte': '',
                # 'pagSgte': '',
                # 'pagAnt': '',
                'pagAct': 0,
                'fechaDesde': '28/09/1991',
                'fechaHasta': '28/09/2021',
                # 'importeDesde': '',
                # 'importeHasta': '',
                'vencDesde': '28/09/2021',
                # 'vencHasta': '',
            })
            yield response.json()

    @lazy_property
    def destination_accounts_page(self):
        page = self.home_page
        section = 'administrarCuentasTransferencia'
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @property
    def destination_accounts(self):
        page = self.destination_accounts_page
        section = 'getCuentasDestinoTransferenciasSinClasificar'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json
        
    def logout(self):
        url = make_url('logout')
        header = bpn_header.logout
        response = self.session.get(url, headers=header)
        json = response.json()
        return json

