from decorator import (
    PostRequest,
    GetRequest,
    json,
    state,
    lazy_property,
)
from requests import Session
from scrapy.http import HtmlResponse
import bpn_header

class Bpn(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = Session()
        self.session.cookies.set('cookieTest', 'true')
        self.pages = {}
        response = self.__login()

    @PostRequest(path='doLogin', headers=bpn_header.login)
    @state(name='login', css='#LoginForm [name="_STATE_"]::attr(value)')
    def __login(self):
        params = {}
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
    @state(name='saldos')
    def accounts(self):
        return dict()

    @lazy_property
    @json
    @PostRequest(path='getCuentasForPC')
    @state(name='posicionConsolidada')
    def accounts_for_pc(self):
        return dict()

    @lazy_property
    @json
    @PostRequest(path='obtenerLinkPagosEnte')
    @state(name='pagosRealizados')
    def entities(self):
        return dict()

    @lazy_property
    @json
    @PostRequest(path='getCuentasDestinoTransferenciasSinClasificar')
    @state(name='administrarCuentasTransferencia')
    def unknown_transfer_accounts(self):
        return dict()

    @lazy_property
    @json
    @PostRequest(path='getPrestamos')
    @state(name='posicionConsolidada')
    def loans(self):
        params = dict()
        params['pageNumber'] = 1
        return params
            # response = self.session.post(url, headers=headers, params={
            #     '_STATE_': state,
            #     'pageNumber': i,
            # })
            # json = response.json()
            # try:
            #     json = json['response']['data']
            #     results.extend(json[0]['consultaPrestamos']['prestamos'])
            # except KeyError:
            #     break

    @lazy_property
    @json
    @PostRequest(path='getCuentasDestinoTransferenciasPropias')
    @state(name='administrarCuentasTransferencia')
    def own_transfer_accounts(self):
        params = dict()
        params['pageNumber'] = 1
        params['linesPerPage'] = 10
        params['pageNumber'] = 1
        params['orderingField'] = 'banco'
        params['sortOrder'] = 'desc'
        return params
            # try:
            #     json = json['response']['data']
            #     results.extend(json)
            # except KeyError:
            #     break

    @lazy_property
    @json
    @PostRequest(path='getCuentasDestinoTransferenciasTerceros')
    @state(name='administrarCuentasTransferencia')
    def third_party_transfer_accounts(self):
        params = dict()
        params['pageNumber'] = 1
        params['linesPerPage'] = 10
        params['pageNumber'] = 1
        params['orderingField'] = 'banco'
        params['sortOrder'] = 'desc'
        return params

    @lazy_property
    @json
    @PostRequest(path='transferenciasByFilter')
    @state(name='resumenTransferencias')
    def transferences(self):
        params = dict()
        params['fechaDesde'] = '01/01/1999'
        params['fechaHasta'] = '30/12/2021'
        params['linesPerPage'] = 100
        params['pageNumber'] = 1
        params['orderingField'] = 'fechaMovimiento'
        params['sortOrder'] = 'desc'
        return params

    @lazy_property
    @json
    @PostRequest(path='getRecargasConsultaCargaValor')
    @state(name='consultaCargaValorTP', css='#consultacargavalorForm [name="_STATE_"]::attr(value)')
    def phone_recharge(self):
        params = dict()
        params['codigoEmpresa'] = ''
        params['usuario'] = ''
        params['canal'] = ''
        params['importe'] = ''
        params['perteneceA'] = ''
        params['fechaDesde'] = '01/01/1999'
        params['fechaHasta'] = '27/09/2021'
        params['pageNumber'] = 1
        params['linesPerPage'] = 5
        params['codigoRubro'] = 'TP'
        return params

    @lazy_property
    @json
    @PostRequest(path='showConsultaCredin')
    @state(name='consultaCredin', css='#grilla::attr(source)')
    def credin(self):
        params = dict()
        params['fechaDesde'] = '01/01/1999'
        params['fechaHasta'] = '30/09/2021'
        params['sentidoCredin'] = 'Enviados'
        params['maxRows'] = 11
        params['page'] = 2
        return params

    @lazy_property
    @json
    @PostRequest(path='getSaldoPosCons')
    @state(name='posicionConsolidada')
    def balance_in_consolidated_position(self):
        for account in self.accounts_for_pc['response']['data']:
            params = dict()
            params['numero'] = account['numero']
            params['tipoTandem'] = account['tipoTandem']
            yield params

    @lazy_property
    @json
    @PostRequest(path='getSaldo')
    @state(name='saldos')
    def balances(self):
        for account in self.accounts['response']['data']:
            params = dict()
            params['numero'] = account['numero']
            params['tipoTandem'] = account['tipoTandem']
            yield params

    @lazy_property
    @json
    @PostRequest(path='getSaldosTotales')
    @state(name='saldos')
    def total_balance(self):
        # required to calculate the total balance
        [_ for _ in self.balances]
        return dict()

    @lazy_property
    @json
    @PostRequest(path='getPagosRealizados')
    @state(name='pagosRealizados', css='#consultaPagosRealizadosForm [name="_STATE_"]::attr(value)')
    def payments_made(self):
        json = self.entities
        for entity in json['response']['data'][0]['adheridos']:
            for i in range(0, 30):
                params = dict()
                params['codAbre'] = entity['codigoAbre']
                params['ente'] = entity['codigoEnte']
                params['linkPagosEnte'] = ''
                params['pagSgte'] = ''
                params['pagAnt'] = ''
                params['pagAct'] = i
                params['fechaDesde'] = '28/09/1991'
                params['fechaHasta'] = '28/09/2021'
                params['importeDesde'] = ''
                params['importeHasta'] = ''
                params['vencDesde'] = '28/09/2021'
                params['vencHasta'] = ''
                yield params
            break

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
    @state(name='login', css='#RedirectHomeForm [name="_STATE_"]::attr(value)')
    def home_page(self):
        return dict()

    def subpage_from_home_page(self, path):
        @PostRequest(path=path)
        @state(name='home', css=f'#_menu_{path}::attr(realhref)')
        def function(self):
            return dict()
        return function(self)

