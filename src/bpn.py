from bs4 import BeautifulSoup as Soup
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from util import lazy_property, make_url, make_regex_state
from decorator import PostRequest, GetRequest, json
import bpn_header
import requests

XPATH_SCRIPT = '//script[contains(. , $text)]/text()'

class Bpn(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.cookies.set('cookieTest', 'true')
        self.pages = {}
        response = self.__login()

    @PostRequest(path='doLogin', headers=bpn_header.login)
    def __login(self, path):
        page = self.page('login')
        selector = '#LoginForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        params = {}
        params['_STATE_'] = state
        params['username'] = self.username
        params['password'] = self.password
        params['jsonRequest'] = True
        params['sfaInfo'] = ''
        params['pcCompartida'] = False
        params['inclu'] = False
        params['recordarUsuario'] = False
        return params

    @GetRequest(path='logout', headers=bpn_header.logout)
    def logout(self, path):
        return dict()

    @lazy_property
    @json
    @PostRequest(path='getCuentas')
    def accounts(self, path):
        page = self.page('saldos')
        regex = make_regex_state(path)
        state = page.xpath(XPATH_SCRIPT, text=path).re_first(regex)
        params = {}
        params['_STATE_'] = state
        return params

    @lazy_property
    @json
    @PostRequest(path='getCuentasForPC')
    def accounts_for_pc(self, path):
        page = self.page('posicionConsolidada')
        regex = make_regex_state(path)
        state = page.xpath(XPATH_SCRIPT, text=path).re_first(regex)
        params = {}
        params['_STATE_'] = state
        return params

    @lazy_property
    def entities(self):
        page = self.page.payments
        section =  'obtenerLinkPagosEnte'
        headers = bpn_header.transferences
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json

    @property
    def unknown_transfer_accounts(self):
        page = self.page.destination_accounts
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
        
    @lazy_property
    def loans(self):
        page = self.page.position
        section =  'getPrestamos'
        headers = bpn_header.transferences
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        results = []
        i = 0
        while True:
            i += 1
            response = self.session.post(url, headers=headers, params={
                '_STATE_': state,
                'pageNumber': i,
            })
            json = response.json()
            try:
                json = json['response']['data']
                results.extend(json[0]['consultaPrestamos']['prestamos'])
            except KeyError:
                break
        return results

    @lazy_property
    def own_transfer_accounts(self):
        page = self.page.destination_accounts
        section = 'getCuentasDestinoTransferenciasPropias'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.transferences
        results = []
        i = 0
        while True:
            i += 1
            response = self.session.post(url, headers=headers, params={
                '_STATE_': state,
                'linesPerPage': 10,
                'pageNumber': i,
                'orderingField': 'banco',
                'sortOrder': 'desc',
            })
            json = response.json()
            try:
                json = json['response']['data']
                results.extend(json)
            except KeyError:
                break
        return results

    @property
    def third_party_transfer_accounts(self):
        page = self.page.destination_accounts
        section = 'getCuentasDestinoTransferenciasTerceros'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.transferences
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
            'linesPerPage': 10,
            'pageNumber': 1,
            'orderingField': 'banco',
            'sortOrder': 'desc',
        })
        json = response.json()
        return json
        
    @property
    def transferences(self):
        page = self.page.transfer_sumary
        section =  'transferenciasByFilter'
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        headers = bpn_header.transferences
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

    @property
    def phone_recharge(self):
        page = self.page.phone_recharge
        section = 'getRecargasConsultaCargaValor'
        selector = '#consultacargavalorForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.transferences
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
    def credin(self):
        page = self.page.credin
        section = 'showConsultaCredin'
        selector = '#grilla'
        state = page.css(selector).xpath('@source').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
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

    # métodos dependientes de los anteriores

    @property
    def total_balance(self):
        # required to calculate the total balance
        [_ for _ in self.balances]
        page = self.page.balance
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

    @lazy_property
    def balance_in_consolidated_position(self):
        page = self.page.position
        section =  'getSaldoPosCons'
        headers = bpn_header.transferences
        regex = make_regex_state(section)
        state = page.xpath(XPATH_SCRIPT, text=section).re_first(regex)
        url = make_url(section)
        response = self.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        json = response.json()
        return json

    # métodos dependientes de los anteriores y con un generador como retorno

    @property
    def balances(self):
        page = self.page.balance
        json = self.accounts
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
    def payments_made(self):
        page = self.page.payments
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

    def page(self, name):
        if name in self.pages:
            page = self.pages[name]
            return page
        if name == 'login':
            response = self.login_page()
        elif name == 'home':
            response = self.home_page()
        else:
            response = self.subpage_from_home_page(name)
        page = HtmlResponse(response.url, body=response.content)
        self.pages[name] = page
        return page

    @PostRequest(path='doLoginFirstStep', headers=bpn_header.login)
    def login_page(self, path):
        params = {}
        params['username'] = self.username
        return params

    @PostRequest(path='home', headers=bpn_header.home)
    def home_page(self, path):
        page = self.page('login')
        selector = '#RedirectHomeForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        params = {}
        params['_STATE_'] = state
        return params

    def subpage_from_home_page(self, section):
        @PostRequest(path=section)
        def function(self, path):
            page = self.page('home')
            selector = f'#_menu_{path}'
            state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
            params = {}
            params['_STATE_'] = state
            return params
        return function(self)

