from bpn import Bpn
import config

username = config.username
password = config.password

bpn = Bpn(username, password)
with open('login.html', 'w', encoding='utf-8') as html:
    text = bpn.soup.prettify()
    html.write(text)

