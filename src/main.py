from bpn import Bpn
import config
from pprint import pprint

username = config.username
password = config.password

bpn = Bpn(username, password)

try:
    result = bpn.phone_recharge()
    print(result)
finally:
    print(bpn.logout())

