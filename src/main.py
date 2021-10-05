from bpn import Bpn
import config
from pprint import pprint

username = config.username
password = config.password

bpn = Bpn(username, password)

try:
    pprint(bpn.accounts_transferences)
finally:
    print(bpn.logout())

