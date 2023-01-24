from flask import Flask, render_template, request, redirect, url_for, Request,session
import requests
import json
from GestorGeocoding import *
import folium
from folium.plugins import MiniMap
from bing_image_downloader import downloader
import pandas as pd
from typing import Literal
import random
import sqlite3


app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

def comprobar_usuario(email, password):
    con = sqlite3.connect('DB.db')
    cur = con.cursor()
    cur.execute('Select email,password FROM Usuarios WHERE email=? and password=?', (email, password))

    result = cur.fetchone()
    if result:
        return True
    else:
        return False


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if comprobar_usuario(email, password):
            #session['email'] = username
            ubicacion_dict = get_coordenadas(request)
            coord = (str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude")))
            city = PeticionCoordenadas(coord)
            urls = get_imagen(city)
            url = urls[0]
            return render_template("principal.html",url=url)

        mensaje = "Username or Password incorrect"   
        return render_template("login.html",mensaje=mensaje)
    else:
        return render_template("login.html")
     

def registro_usuarios(name,email,password):
    if name == "" or email=="" or password=="":
        return render_template('registro.html')

    con = sqlite3.connect('DB.db')
    cur = con.cursor()
    cur.execute('INSERT INTO Usuarios(nombre,email,password,gustos,foto) values (?,?,?,?,?)', (name,email,password,None,None))
    con.commit()

    result = cur.fetchone()
    con.close()
    if result:
        return True
    else:
        return False

@app.route("/registro", methods=["POST", "GET"])
def registro():
    if request.method == 'POST':
        nombre = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if registro_usuarios(nombre,email,password):
            return render_template("login.html")
        else:
            mensaje = "User already exists"
            return render_template('registro.html',mensaje=mensaje)
    else:
        return render_template('registro.html')


@app.route("/principal", methods=["POST","GET"])
def principal():
    ubicacion_dict = get_coordenadas(request)
    coord = (str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude")))
    city = PeticionCoordenadas(coord)
    urls = get_imagen(city)
    url = urls[0]
    return render_template("principal.html",url=url)
    


@app.route("/eventos")
def eventos():
    API_KEY = "FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA"
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?classificationName=music&city=Madrid&apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA"
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("_embedded")

    eventos = info.get("events")
    get_image = lambda event: event["images"][-1]

    return render_template(
        "eventos.html", eventos=eventos, get_img=get_image
    )  # Enviamos los datos que queremos mostrar en el html5 list es el atributo que queremos de la api


@app.route("/eventosUbic", methods=["POST"])
def eventosPorUbicacion():
    ubic = request.form[
        "search"
    ]  # De esta manera obtengo la ubicacion introducida por el usuario en el html
    # API_KEY = "FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA"
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?city="
        + ubic
        + "&apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA"
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("_embedded")

    if datosFormatonJSON == None or info == None:
        return render_template("eventos.html")

    eventos = info.get("events")
    get_image = lambda event: event["images"][-1]

    return render_template("eventosUbic.html", eventos=eventos, get_img=get_image)


@app.route("/noticias")
def Noticias():
    API_KEY = "pub_7421c00b07c3b0a1ab68df5be83ae037be9f"
    datosObtenidos = requests.get(
        "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news&language=es"
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("results")

    return render_template("noticias.html", noticias=info)


@app.route("/noticiasUbic", methods=["POST"])
def NoticiasPorUbic():
    API_KEY = "pub_7421c00b07c3b0a1ab68df5be83ae037be9f"
    ubic = request.form[
        "search"
    ]  # De esta manera obtengo la ubicacion introducida por el usuario en el html
    datosObtenidos = requests.get(
        "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news%20AND%20"
        + ubic
        + "&language=es"
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("results")

    return render_template("noticiasUbic.html", noticias=info)


@app.route("/meterologiaUbic")
def meterologiaUbic():
    ubicacion_dict = get_coordenadas(request)
    coord = (
        str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude"))
    )

    city = PeticionCoordenadas(coord)
    datosObtenidos = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q="
        + city
        + "&appid=8ca0c1c6f4748e36b8463b280a518364&units=Metric&lang=es"
    )
    datosFormatonJSON = datosObtenidos.json()
    if datosFormatonJSON.get("message") != None:
        return render_template("meterologia.html")

    info = datosFormatonJSON.get("main")
    weather = datosFormatonJSON.get("weather")[0]

    meterologia = {
        "city": city,
        "description": weather["description"],
        "clim": weather["main"],
        "icon": weather["icon"],
        "temp": info["temp"],
        "temp_min": info["temp_min"],
        "temp_max": info["temp_max"],
        "pressure": info["pressure"],
        "humidity": info["pressure"],
        "windspeed": datosFormatonJSON["wind"]["speed"],
    }

    return render_template("meterologiaUbic.html", weather=meterologia)


def get_coordenadas(request: Request):
    coordenadas = request.cookies.get("ubicacion")
    if coordenadas == None:
        return
    coordenadas = json.loads(coordenadas)
    return coordenadas


def get_imagen(
    city
):
    url = "https://bing-image-search1.p.rapidapi.com/images/search"
    count = 10
    params = {"q": city, "count": count, "mkt": "es-ES"}

    headers = {
        "X-RapidAPI-Key": "ac908a072dmshb0c322cb20afca5p1837b4jsne3ed0bbb1d53",
        "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=params)

    data = response.json()

    results = data["value"]

    index = random.randint(0,count-1)
    img = results[index]

    return img["contentUrl"], img["thumbnailUrl"]


@app.route("/mapa")
def mapa():
    ubicaciones = {
        "Madrid": [40.463667, -3.74922],
        "Caceres": [39.47649, -6.37224],
        "Burgos": [42.3502200, -3.6752700],
    }

    mapa = folium.Map(
        location=[40.463667, -3.74922], zoom_start=6.45, control_scale=True
    )  # Carga el mapa de Espana

    for ubic in ubicaciones:
        ubicacion = "<b>"
        ubicacion += ubic
        ubicacion += "</b>"

        coordenadas = ubicaciones.get(ubic)

        # Ubicaciones de las cuales se muestran los eventos y noticias en el mapa
        folium.Marker(location=coordenadas, popup=ubicacion).add_to(mapa)
        # Colocamos el icono de ubicacion
        folium.Circle(
            location=coordenadas,
            color="purple",
            fill_color="red",
            radius=50,
            weight=4,
            fill_opacity=0.5,
            tooltip=ubicacion,
        ).add_to(mapa)

    minimapa = MiniMap()
    mapa.add_child(minimapa)
    mapa.save(
        "templates/mapa.html"
    )

    return render_template("mapa.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

