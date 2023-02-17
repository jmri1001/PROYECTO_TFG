import requests
from datetime import datetime, date
from deep_translator import GoogleTranslator
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, Request,session
import random
import json
from os import remove
import sqlite3
import folium
from folium.plugins import MiniMap



#Funcion que devuelve el dia de la semana respecto a una fecha pasada como parametro
def Fecha_d(fecha):
    date_sr = str(pd.to_datetime(fecha))
    dt = datetime.fromisoformat(date_sr)
    dia_Semana = dt.strftime("%A")
    traductor = GoogleTranslator(source='en', target='es')
    resultado = traductor.translate(dia_Semana)
    return resultado

def Evento_Favorito(nombre,PrecioMin,PrecioMax,fecha,ciudad,direccion,venues,imagen,latitud,longitud):
    # Añadimos a la base de datos el evento elegido por el usuario como favorito 
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT count(Nombre) FROM EventosFavoritos WHERE Nombre=?", (nombre,))
    resul = cur.fetchall()
    count = resul[0][0]
    con.close()

    if count == 0:
        con = sqlite3.connect("DB.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO EventosFavoritos(Nombre,PrecioMax,PrecioMin,Fecha,Ciudad,Direccion,Imagen,Venues,Latitud,Longitud) values (?,?,?,?,?,?,?,?,?,?)",
            (nombre,PrecioMax,PrecioMin,fecha,ciudad,direccion,imagen,venues,latitud,longitud),
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

    if (coordenadas == "42.3443701,-3.6927629"):
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


