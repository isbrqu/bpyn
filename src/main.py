from bpn import Bpn
import config
from pprint import pprint

username = config.username
password = config.password

bpn = Bpn(username, password)

try:
    for balance in bpn.balances:
        print(balance)
    # result = bpn.balances()
    # print(result)
finally:
    print(bpn.logout())

