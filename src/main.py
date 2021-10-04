from bpn import Bpn
import config
from pprint import pprint

username = config.username
password = config.password

bpn = Bpn(username, password)

try:
    pprint(bpn.total_balance)
finally:
    print(bpn.logout())

