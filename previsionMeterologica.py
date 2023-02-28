import requests
from datetime import datetime, date
from deep_translator import GoogleTranslator
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, Request,session,flash
import random
import json
from os import remove
import sqlite3
import folium
from folium.plugins import MiniMap
import os
from GestorGeocoding import *
from bing_image_downloader import downloader
from typing import Literal
from previsionMeterologica import *
from urllib.parse import parse_qsl


def comprobar_usuario(email, password):
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute(
        "Select email,password FROM Usuarios WHERE email=? and password=?",
        (email, password),
    )

    result = cur.fetchone()
    if result:
        return True
    else:
        return False


def registro_usuarios(name, email, password):

    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT count(email) FROM Usuarios WHERE email=?", (email,))
    resul = cur.fetchall()
    count = resul[0][0]
    con.close()

    if count == 0:
        con = sqlite3.connect("DB.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Usuarios(nombre,email,password,gustos,foto) values (?,?,?,?,?)",
            (name, email, password, None, None),
        )
        con.commit()
        result = cur.fetchone()
        con.close()
        return True

    return False


def get_coordenadas(request: Request):
    coordenadas = request.cookies.get("ubicacion")
    if coordenadas == None:
        return
    coordenadas = json.loads(coordenadas)
    return coordenadas


def UbicacionTiempoReal():
    ubicacion_dict = get_coordenadas(request)
    coord = (
        str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude"))
    )
    coord = coord.split(',',1)
    latitud = float(coord[0])
    longitud = float(coord[1])
    
    mapa = folium.Map(location=[latitud,longitud],zoom_start=11.5, control_scale=True)   #Carga el mapa de Espana
    # #Ubicacion actual del usuario
    folium.Marker(location=[latitud,longitud],icon=folium.Icon(color='lightgreen')).add_to(mapa)
    # #Colocamos el icono de ubicacion 
    folium.Circle(location=[latitud,longitud],color="purple",fill_color="red",radius=50,weight=4,fill_opacity=0.5).add_to(mapa) 
    mapa.save("templates/ubicacionReal.html")


#Funcion que devuelve el dia de la semana respecto a una fecha pasada como parametro
def Fecha_d(fecha):
    date_sr = str(pd.to_datetime(fecha))
    dt = datetime.fromisoformat(date_sr)
    dia_Semana = dt.strftime("%A")
    traductor = GoogleTranslator(source='en', target='es')
    resultado = traductor.translate(dia_Semana)
    return resultado

def Evento_Favorito(nombre,PrecioMin,PrecioMax,fecha,ciudad,direccion,venues,imagen,latitud,longitud,usuario):
    # Añadimos a la base de datos el evento elegido por el usuario como favorito 
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT count(Nombre) FROM EventosFavoritos WHERE Nombre=? AND Ciudad=?", (nombre,ciudad,))
    resul = cur.fetchall()
    count = resul[0][0]
    con.close()

    if count == 0:
        con = sqlite3.connect("DB.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO EventosFavoritos(Nombre,PrecioMax,PrecioMin,Fecha,Ciudad,Direccion,Imagen,Venues,Latitud,Longitud,IdUsuario) values (?,?,?,?,?,?,?,?,?,?,?)",
            (nombre,PrecioMax,PrecioMin,fecha,ciudad,direccion,imagen,venues,latitud,longitud,usuario),
        )
        con.commit()
        result = cur.fetchone()
        con.close()
        return True

    return False

#Llamada de datos meterologicos para hacer un grafico por horas
def Prevision_Clima(city):

    datosObtenidos = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q=" + city + "&cnt=8&appid=8ca0c1c6f4748e36b8463b280a518364&units=Metric&lang=es"
        )
    datosFormatonJSON = datosObtenidos.json()

    lista = []
    info = {}
    temperatura = []
    por_horas = []

    lista_weather = datosFormatonJSON.get("list")
    # print(lista_weather)

    for weather in lista_weather:
        temp = weather.get("main").get("temp")
        temp = str(round(temp))+"ºC"
        descr = weather.get("weather")[0].get("description")
        date = weather.get("dt_txt")
        valor = date.split(" ",1)
        hora = valor[1][:5]

        info = {
            "temp": temp,
            "icono": weather.get("weather")[0].get("icon"),
            "lluvia": weather.get("pop"),
            "fecha": hora,
            "descripcion": descr
        }
        temperatura.append(temp)    
        por_horas.append(hora)
        lista.append(info)

    return (temperatura,por_horas,lista)


def climaDia(coordenadas):

    if (coordenadas == "42.3443701,-3.6927629" or coordenadas == "42.34995,-3.69205"):
        coordenadas = "41.6704100,-3.6892000"

    datosObtenidos = requests.get( "https://api.tutiempo.net/json/?lan=es&&units=Metric&apid=XwY44q4zaqXbxnV&ll=" + coordenadas)
    datosFormatonJSON = datosObtenidos.json()

    dias = []
    dias.append(datosFormatonJSON.get("day2"))
    dias.append(datosFormatonJSON.get("day3"))
    dias.append(datosFormatonJSON.get("day4"))
    dias.append(datosFormatonJSON.get("day5"))
    dias.append(datosFormatonJSON.get("day6"))
    dias.append(datosFormatonJSON.get("day7"))

    if None in dias:
        return None

    lista = []
    url = "https://v5i.tutiempo.net"
    wd, wi = f"{url}/wd/big/black/", f"{url}/wi/"
    wi_icon = wi + "{style}/{size}/{icon}.png"
    wd_icon = wd + "{icon}.png"

    for d in dias:
        date = d.get("date")
        temp_min = d.get("temperature_min")
        temp_max = d.get("temperature_max")
        icono = d.get("icon")
        viento = d.get("wind")
        icono_viento = d.get("icon_wind")

        info = {
                "fecha": date,
                "temp_min": temp_min,
                "temp_max": temp_max,
                "icono": icono,
                "viento": viento,
                "icono_viento": icono_viento,
                "wi_icon": wi_icon,
                "wd_icon": wd_icon 
            }

        lista.append(info)

    return lista

#para hacer el grafico
# lista = Prevision_Clima("Burgos")
# x = lista[0]
# y = lista[1]
# print(lista)
# plt.plot(x,y)
# plt.show()

def Preparese_Para_Su_Dia(city):
    lista = Prevision_Clima("Burgos")
    datos = lista[2][0]
    info = {}
 
    today = date.today()
    fecha = today.strftime("%a, %d %b %Y")
    paraguas = "No es necesario"
    abrigo = "Ropa fina"
    sensacion_termica = datos.get("temp")
    al_aire_libre = datos.get("descripcion")
    temp = datos.get("temp")
    temp = temp.split("º",1)

    if datos.get("lluvia") > 30:
        paraguas = "Es necesario"
    if int(temp[0]) < 14:
        abrigo = "Ropa gruesa"
    if int(temp[0]) > 23:
        abrigo = "Ropa de verano"
    
    info = {
            "paraguas": paraguas,
            "abrigo": abrigo,
            "sensTermica": sensacion_termica,
            "aireLibre": al_aire_libre,
            "fecha": fecha
        }
    
    return info


def load_file_json_events():
    with open('eventos.json', 'r') as fp:
        data = json.load(fp)
        return data


def save_file_json_events(my_dict):
    remove("eventos.json")
    with open('eventos.json', 'w') as fp:
        json.dump(my_dict, fp)
    

def load_file_json_news():
    with open('noticias.json', 'r') as fp:
        data = json.load(fp)
        return data


def save_file_json_news(my_dict):
    remove("noticias.json")
    with open('noticias.json', 'w') as fp:
        json.dump(my_dict, fp)


def Eventos(id):
    # Extraemos de la base de datos los eventos elegidos por el usuario como favoritos 
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()
    con.close()
    
    mapa = folium.Map(location=[40.463667,-3.74922],zoom_start=6.45, control_scale=True)   #Carga el mapa de Espana

    for tupla in resul:
        latitud = tupla[8]
        longitud = tupla[9]
        ubicacion = tupla[7]
        evento = "<b>Evento: "
        evento += tupla[0]
        evento += "</b>"
        
        #Ubicaciones de las cuales se muestran los eventos y noticias en el mapa
        folium.Marker(location=[latitud,longitud],popup=evento,icon=folium.Icon(color='lightgreen')).add_to(mapa)
        #Colocamos el icono de ubicacion 
        folium.Circle(location=[latitud,longitud],color="purple",fill_color="red",radius=50,weight=4,fill_opacity=0.5,tooltip=ubicacion).add_to(mapa) 
    
    minimapa = MiniMap()
    mapa.add_child(minimapa)

    mapa.save("templates/mapa.html")


def Eventos_DB_Mapa(id):
    # Extraemos de la base de datos los eventos elegidos por el usuario como favoritos 
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()
    con.close()
    return resul

def BorrarEventoFav(nombre,ciudad):
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("DELETE FROM EventosFavoritos WHERE Nombre=? AND Ciudad=?", (nombre,ciudad,))
    con.commit()
    con.close()


def get_imagen(city):
    url = "https://bing-image-search1.p.rapidapi.com/images/search"
    count = 4
    params = {"q": city, "count": count, "mkt": "es-ES"}

    headers = {
        "X-RapidAPI-Key": "275bb62fcfmshe06f494e237a78cp174832jsn0dbb9c290237",
        "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=params)

    data = response.json()

    results = data["value"]

    index = random.randint(0, count - 1)
    img = results[index]

    return img["contentUrl"], img["thumbnailUrl"]


def NoticiasApi():
    API_KEY = "pub_7421c00b07c3b0a1ab68df5be83ae037be9f"
    datosObtenidos = requests.get(
        "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news&language=es&country=es"
    )
    datosFormatonJSON = datosObtenidos.json()

    if (not "totalResults" in datosFormatonJSON) or int(
        datosFormatonJSON.get("totalResults")
    ) <= 5:
        datosFormatonJSON = load_file_json_news()
    else:
        save_file_json_news(datosFormatonJSON)

    return datosFormatonJSON.get("results")

def infoEventosApi(idEvento):
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&id=" + idEvento
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("_embedded")
    evento = info.get("events")[0]


    nombre = evento.get("name")
    imagen = evento.get("images")[0].get("url")
    precioMin = 0
    precioMax = 0
    if "priceRanges" in evento:
        precioMin = evento.get("priceRanges")[0].get("min")
        precioMax = evento.get("priceRanges")[0].get("max")

    fecha = evento.get("dates").get("start").get("localDate")
    masInfo = evento.get("_embedded")
    ciudad = masInfo.get("venues")[0].get("city").get("name")
    direccion = masInfo.get("venues")[0].get("address").get("line1")
    venues = masInfo.get("venues")[0].get("name")
    latitud = masInfo.get("venues")[0].get("location").get("latitude")
    longitud = masInfo.get("venues")[0].get("location").get("longitude")

    infoEvento = {"nombre":nombre,
                  "PrecioMin":precioMin,
                  "PrecioMax":precioMax,
                  "Fecha":fecha,
                  "Ciudad":ciudad,
                  "Direccion":direccion,
                  "Venues":venues,
                  "Imagen":imagen,
                  "Latitud":latitud,
                  "Longitud": longitud}
    
    return infoEvento

def eventosApi():
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&language=es&countryCode=ES"
    )
    datosFormatonJSON = datosObtenidos.json()

    if (datosFormatonJSON.get("page").get("totalElements") == 0) or (
        int(datosFormatonJSON.get("page").get("totalElements")) < 5
    ):
        datosFormatonJSON = load_file_json_events()
    else:
        save_file_json_events(datosFormatonJSON)

    info = datosFormatonJSON.get("_embedded")

    eventos = info.get("events")
    get_image = lambda event: event["images"][-1]
    get_categoria = lambda categ: categ["classifications"][0]["segment"]

    return (eventos,get_image,get_categoria)