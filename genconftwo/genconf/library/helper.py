import string
import re
from random import Random
from urllib.request import urlopen

ESCAPE_REGEX = re.compile(r"[\0\n\r\032\'\"\\]")
ESCAPE_MAP = {'\0': '\\0', '\n': '\\n', '\r': '\\r', '\032': '\\Z',
              '\'': '\\\'', '"': '\\"', '\\': '\\\\'}

def sub_domain_to_domain(domains, sub_domain_to_find):
    result = None
    for domain in domains.keys():
        for subdomain in domains[domain]:
            if subdomain == sub_domain_to_find:
                result = domain
    return result

def make_password(password_length):
    charlist = list(string.digits + string.ascii_letters)
    result = ''
    r = Random()
    url = "http://www.random.org/integers/?num=2" + \
                "&min=1&max=1000000000&col=1&base=10&format=plain&rnd=new"
    f = urlopen(url)
    number = f.read().decode("utf-8").replace("\n", "")
    r.seed(int(number))
    r.shuffle(charlist)
    for dummy in range(password_length):
        result += r.choice(charlist)
    return result

def escape_string(value):
    return ESCAPE_REGEX.sub(
            lambda match: ESCAPE_MAP.get(match.group(0)), value)