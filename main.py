from bpn import Bpn
import config

username = config.username
password = config.password

bpn = Bpn(username, password)
# with open('home.html', 'w', encoding='utf-8') as html:
#     text = bpn.soup.prettify()
#     html.write(text)
try:
    for item in bpn.positions():
        print(item)
except Exception as exception:
    print(exception)
finally:
    print(bpn.logout())

