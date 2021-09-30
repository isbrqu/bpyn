scheme = 'https'
domain = 'hb.redlink.com.ar'
directory = 'bpn'
base = f'{scheme}://{domain}/{directory}'
position = f'{base}/posicionConsolidada.htm'
accounts = f'{base}/getCuentasForPC.htm'
balance = f'{base}/getSaldoPosCons.htm'
logout = f'{base}/logout.htm'
movements = f'{base}/movimientosHistoricos.htm'

def make(name):
    return f'{base}/{name}.htm'
