from bpn import Bpn
import config
from pprint import pprint

username = config.username
password = config.password

bpn = Bpn(username, password)

try:
    # pprint(bpn.payments_made)
    [pprint(payments_made) for payments_made in bpn.payments_made]
finally:
    print(bpn.logout())

