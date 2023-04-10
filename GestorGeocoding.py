import requests
from geopy.geocoders import Nominatim
from functools import partial


def PeticionCoordenadas(coordenadas):
    geolocator = Nominatim(user_agent="joselii6ito@gmail.com")
    geocode = partial(geolocator.reverse, language="es")
    info = geocode(coordenadas)
    if info != None:
        address = info.raw["address"]
        city: str = address.get("city") or address.get("village")
        print(f"Info de {city}: ")
        return city
    else:
        return None


def PeticionToponimo(city):
    geolocator = Nominatim(user_agent="joselii6ito@gmail.com")
    location = geolocator.geocode(city, language="es", country_codes="ES")
    if location != None:
        latitud = str(location.latitude)
        longitud = str(location.longitude)
        latitud += "," + longitud
        return latitud
    else:
        return None


# coordenadas = "38.9977" + "," + "1.4305"
# PeticionCoordenadas(coordenadas)
