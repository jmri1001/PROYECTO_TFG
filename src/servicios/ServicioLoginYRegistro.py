from datetime import datetime
from deep_translator import GoogleTranslator
import pandas as pd
from flask import request, Request
import json
import folium
import bcrypt
from geopy.geocoders import Nominatim
from functools import partial
from ..db import con
from ..utils import relative_to



def comprobar_usuario(email, pass_texto_plano):
    cur = con.cursor()
    cur.execute(
        "Select password FROM Usuarios WHERE email=?",
        (email,),
    )
    result = cur.fetchall()

    if len(result) == 0: return False

    pass_hasheada = result[0][0]
    pass_texto_plano = pass_texto_plano.encode()   
    if bcrypt.checkpw(pass_texto_plano, pass_hasheada):
        return True
    else:
        return False
    

def registro_usuarios(name, email, password):
    cur = con.cursor()
    cur.execute("SELECT count(email) FROM Usuarios WHERE email=?", (email,))
    resul = cur.fetchall()
    count = resul[0][0]
    
    if count == 0:
        password = password.encode()
        sal = bcrypt.gensalt()
        pass_hasheada = bcrypt.hashpw(password, sal)

        cur.execute(
            "INSERT INTO Usuarios(nombre,email,password,gustos,foto) values (?,?,?,?,?)",
            (name, email, pass_hasheada, None, None),
        )
        result = cur.fetchone()
        con.commit()
        return True
    
    con.commit()
    return False

def get_coordenadas(request: Request):
    coordenadas = request.cookies.get("ubicacion")
    if coordenadas == None:
        return
    coordenadas = json.loads(coordenadas)
    print(coordenadas)
    return coordenadas


def UbicacionTiempoReal():
    ubicacion_dict = get_coordenadas(request)
    coord = (
        str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude"))
    )
    coord = coord.split(",", 1)
    latitud = float(coord[0])
    longitud = float(coord[1])

    mapa = folium.Map(
        location=[latitud, longitud], zoom_start=11.5, control_scale=True
    )  # Carga el mapa de Espana
    # #Ubicacion actual del usuario
    folium.Marker(
        location=[latitud, longitud], icon=folium.Icon(color="lightgreen")
    ).add_to(mapa)
    # #Colocamos el icono de ubicacion
    folium.Circle(
        location=[latitud, longitud],
        color="purple",
        fill_color="red",
        radius=50,
        weight=4,
        fill_opacity=0.5,
    ).add_to(mapa)
    mapa.save("templates/ubicacionReal.html")


def Fecha_d(fecha):
    date_sr = str(pd.to_datetime(fecha))
    dt = datetime.fromisoformat(date_sr)
    dia_Semana = dt.strftime("%A")
    traductor = GoogleTranslator(source="en", target="es")
    resultado = traductor.translate(dia_Semana)
    return resultado


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
