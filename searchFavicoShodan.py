#!/usr/bin/python3
# -*- coding: utf-8 -*-
# by @nuria_imeq
'''
Los navegadores modernos muestran una pequeña imagen (icono) en el lado izquierdo
del titulo de la pagina web. Ese icono se conoce como favicon.ico
Este programa calcula el hash del favicon.ico de un servicio oculto y lo buscara en shodan.
Para buscar usa tor por lo que puedes buscar favicon.ico en servicios ocultos.

NOTA: Usa la API de Shodan para buscar. Debes de incluir tu API de desarrollador.

Mejoras:
    Que la busqueda sea argumento, hay veces que necesitas acotar la busqueda en shodan
'''

import argparse
import requests


from stem import Signal
from stem.control import Controller
from colorama import init, Fore, Back, Style
import mmh3,base64
from shodan import Shodan

'''
Referencias:
https://isc.sans.edu/forums/diary/Hunting+phishing+websites+with+favicon+hashes/27326/
'''

proxies = {
    # uso socks5h protocol
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def parserArgument():
    parser = argparse.ArgumentParser(
            description = 'Busca el hash del fichero favicon.ico en Shodan',
            prog = 'searchFavicoShodan.py', usage='%(prog)s [-h]'
    )
    parser._optionals.title = "Opciones:"
    parser.add_argument("-u", "--url", help="url", required = True)
    parser.add_argument("-v", "--verbose",   help="output verbose", action="store_true")
    parser.add_argument("-V", "--version", action='version', version='%(prog)s version 1.0')
    args = parser.parse_args()
    return args.url

def newTorIdentity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        print("Success!! New Tor connection")
        controller.close()

def startTorSession():
    session = requests.session()
    session.proxies = proxies
    return session

def searchShodan(fav):
    api = Shodan('API')
    search = 'http.favicon.hash:' + str(fav)
    print('Busqueda en Shodan ' + Fore.RED + search)
    for icons in api.search_cursor(search):
        print(icons)

def main():
    header = {}
    user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
    header['User-Agent'] = user_agent
    url = parserArgument()
    if url[-1] == '/':
        url = url.rstrip(url[-1])

    url = url + '/favicon.ico'
    newTorIdentity()
    session = startTorSession()
    r = session.get(url, headers = header)
    if ( r.status_code == 404 ):
        print ('No existe fichero ' + Fore.RED + 'favicon.ico ' + Style.RESET_ALL + 'en url ' + Fore.RED + url)
        exit()
  
    r = session.get(url, headers = header).content
    f_b64 = base64.encodebytes(r)
    favicon = mmh3.hash(f_b64)
    searchShodan(favicon)

if __name__ == "__main__":
    main()
