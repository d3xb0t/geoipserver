import psutil
import geocoder
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

url = 'https://api.abuseipdb.com/api/v2/check'
app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def _geocoder(ip):
    """Funcion que recibe una IP y retorna latitud y longitud
       usando el modulo geocoder
    Args:
        ip (string): Direccion ip 
    Returns:
        Array: Array que contiene latitud y longitud
    """
    g = geocoder.ip(ip)
    return g.latlng

def integrity(ip):
    """Funcion que recibe una IP y utiliza la API de AbuseIp la cual
       returna la reputacion de la ip
    Args:
        ip (string): Direccion ip
    Returns:
        String, objeto Json: Contiene la respuesta proveniente de AbuseIp
    """
    querystring = {
    'ipAddress': ip,
    'maxAgeInDays': '90'
    }
    headers = {
    'Accept': 'application/json',
    'Key': 'TU API-KEY'
    }
    response = requests.request(method='GET', url=url, headers=headers, params=querystring)
    decodedResponse = json.loads(response.text)
    return decodedResponse


def getIps():
    """Funcion que hace una query al modulo psutil y retornar las direcciones ip de las maquinas
       conectadas a nuestro servidor
    Returns:
        Array: Contiene las ip de las maquinas remotas en una lista
    """
    connections = psutil.net_connections()
    list = []
    for c in connections:
        if (len(c[4]) >= 1) and ("192.168" not in c[4][0]) and ("172.17" not in c[4][0]) and ("2800:e2:4e80:10bd:60f0:8302:2c84:6c1" not in c[4][0]) and ("2800:e2:4e80:10bd:9f1d:f91:e080:2903" not in c[4][0]) and ("fe80::f621:dbae:fe45:f689" not in c[4][0]) and ("127.0.0" not in c[4][0]):
           list.append(c[4][0])
    return list


@app.get('/')
async def _main():
    """Root, direccion usada para comprobar estado del servidor
    Returns:
        Objeto: Json
    """
    return {"success": "Its A Live"}

@app.get('/integrity')
async def _integrity():
    """/integrity, direccion usada para extraer reputacion de las ip conectadas de manera remota
        al servidor
    Returns:
        Objeto : Json
    """
    data = getIps()
    print(data)
    integrityResponse = {ip:[integrity(ip), _geocoder(ip)] for ip in data}
    return {"payload": integrityResponse}

@app.get('/geolocate')
async def _geoLocate():
    """/geolocate, direccion usada para extraer localizacion y numero de reportes hechos
        a una ip
    Returns:
        Objeto: Json
    """
    data = getIps()
    integrityResponse = {ip:integrity(ip) for ip in data}
    latlng = {ip:[_geocoder(ip), integrityResponse[ip]['data']['totalReports'] ] for ip in data}
    return latlng


