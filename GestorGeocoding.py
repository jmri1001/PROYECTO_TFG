import requests
from geopy.geocoders import Nominatim
from functools import partial


def PeticionCoordenadas(coordenadas):
        geolocator = Nominatim(user_agent= 'joselii6ito@gmail.com')
        geocode = partial(geolocator.geocode, language="es")
        info = geocode(coordenadas)
        if info != None:
                info = str(info)
                valores = info.split(',',4)
                return valores[3]
        else:
                return None

def PeticionToponimo(city):
        geolocator = Nominatim(user_agent= 'joselii6ito@gmail.com')
        location = geolocator.geocode(city,language="es",country_codes="ES")
        if location != None:
                latitud = str(location.latitude)
                longitud = str(location.longitude)
                latitud += "," + longitud
                return  latitud
        else:
                return None
        


geolocator = Nominatim(user_agent= 'joselii6ito@gmail.com')
geocode = partial(geolocator.geocode, language="es")
info = geocode("42.34,-3.70")
info.raw
print(info)










