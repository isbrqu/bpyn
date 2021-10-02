from bs4 import BeautifulSoup as Soup
import bpn_header
import re
import requests
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

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

class Bpn(object):

    def __init__(self, username, password, is_inclu=False, pin=''):
        self.username = username
        self.session = requests.Session()
        self.session.cookies.set('cookieTest', 'true')
        self.__login(username, password, is_inclu, pin)

    def __login(self, username, password, is_inclu, pin):
        # first login
        section = 'doLoginFirstStep'
        url = make_url(section)
        headers = bpn_header.login
        response = self.session.post(url, headers=headers, params={
            'isInclu': is_inclu,
            'username': username,
            'pin': pin,
        })
        page = HtmlResponse(url, body=response.content)
        # second login
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
            'pcCompartida': True,
            'inclu': False,
            'recordarUsuario': False,
        })
        # entry to home
        section = 'home'
        selector = '#RedirectHomeForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.home
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        self.home = HtmlResponse(url, body=response.content)

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

    def credin(self):
        selector = '#_menu_consultaCredin'
        state = realhref_state(self.soup_home, selector)
        # next
        params = {
            '_STATE_': state,
        }
        url = make_url('consultaCredin')
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
        url = make_url(section)
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
        # first request
        section = 'consultaCargaValorTP'
        selector = f'#_menu_{section}'
        state = self.home.css(selector).xpath('@realhref').re_first(r'=(.*)')
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

    def transferences(self):
        section = 'resumenTransferencias'
        selector = f'#_menu_{section}'
        state = self.home.css(selector).xpath('@realhref').re_first(r'=(.*)')
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

    def payments_made(self):
        section = 'pagosRealizados'
        selector = f'#_menu_{section}'
        attr = 'realhref'
        state = extract_state(self.soup_home, selector=selector, attr=attr)
        params = {
            '_STATE_': state,
        }
        url = make_url(section)
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
        url = make_url(section)
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
        url = make_url(section)
        header = bpn_header.balance
        response = self.session.post(url, params=params, headers=header)
        json = response.json()
        return json

    def accounts_transferences(self):
        pass

    def logout(self):
        url = make_url('logout')
        header = bpn_header.logout
        response = self.session.get(url, headers=header)
        json = response.json()
        return json

