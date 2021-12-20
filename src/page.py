from bs4 import BeautifulSoup as Soup
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from util import lazy_property, make_url, make_regex_state
import bpn_header
import requests

class Page(object):

    menu_item = {
        'credin': 'consultaCredin',
        'balance': 'saldos',
        'payments': 'pagosRealizados',
        'destination_accounts': 'administrarCuentasTransferencia',
        'transfer_sumary': 'resumenTransferencias',
        'phone_recharge': 'consultaCargaValorTP',
        'position': 'posicionConsolidada',
        'last_movements': 'ultimosMovimientos',
        'movements_of_the_day': 'movimientosDia',
        'tendences': 'posicion31DicWS',
        'cbu': 'consultaCbu',
        'buys': 'consultasComprasComercios',
        'creditcards': 'consultaTarjetasCredito',
        'documents': 'gestionDocumentosElectronicosConsulta',
        'movements': 'movimientosHistoricos',
    }

    def __init__(self, bpn):
        self.bpn = bpn

    # usado únicamente para las páginas de home
    def __getattr__(self, attr):
        section = Page.menu_item.get(attr, None)
        if section:
            page = self.__item_menu_home(section)
            setattr(self, attr, page)
            return page
        cname = self.__class__.__name__
        raise AttributeError(f"'{cname}' object has no attribute '{attr}'")

    @lazy_property
    def login(self):
        section = 'doLoginFirstStep'
        url = make_url(section)
        headers = bpn_header.login
        response = self.bpn.session.post(url, headers=headers, params={
            'username': self.bpn.username,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    def __post_state(self, url, headers, state):
        response = self.bpn.session.post(url, headers=headers, params={
            '_STATE_': state,
        })
        page = HtmlResponse(url, body=response.content)
        return page

    @lazy_property
    def home(self):
        page = self.login
        section = 'home'
        selector = '#RedirectHomeForm [name="_STATE_"]'
        state = page.css(selector).attrib['value']
        url = make_url(section)
        headers = bpn_header.home
        return self.__post_state(url, headers, state)

    def __item_menu_home(self, section):
        page = self.home
        selector = f'#_menu_{section}'
        state = page.css(selector).xpath('@realhref').re_first(r'=(.*)')
        url = make_url(section)
        headers = bpn_header.transferences
        return self.__post_state(url, headers, state)

