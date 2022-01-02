from bpn import Bpn
import config
from pprint import pprint
import yaml

username = config.username
password = config.password

try:
    bpn = Bpn(username, password)
    # value = bpn.b
    # print(value)
    # value = values
    for value in bpn.third_party_transfer_accounts:
        for data in value['response']['data']:
            pertenece = data['perteneceA']
            cbu = data['numeroCbu']
            # print(yaml.dump(value))
            print(cbu, pertenece)
    # print(yaml.dump(value))
    # value = bpn.accounts
    # print(yaml.dump(value))
    # value = bpn.accounts_for_pc
    # print(yaml.dump(value))
    # value = bpn.entities
    # print(yaml.dump(value['response']['data'][0]['adheridos']))
    # value = bpn.unknown_transfer_accounts
    # print(yaml.dump(value))
    # print(value)
    # print('='*20)
finally:
    page = bpn.logout()
    print(page.url)

