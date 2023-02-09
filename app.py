from flask import Flask, render_template, request, redirect, url_for, Request, session
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
from previsionMeterologica import *
from urllib.parse import parse_qsl


app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")


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


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if comprobar_usuario(email, password):
            # session['email'] = username
            ubicacion_dict = get_coordenadas(request)
            coord = (
                str(ubicacion_dict.get("latitude"))
                + ","
                + str(ubicacion_dict.get("longitude"))
            )
            city = PeticionCoordenadas(coord)
            # urls = get_imagen(city)
            # url = urls[0]
            url = ""
            return render_template("principal.html", url=url)

        elif email != "" or password != "":
            mensaje = "Username or Password incorrect"
            return render_template("login.html", mensaje=mensaje)
        else:
            return render_template("login.html")

    else:
        ubicacion_dict = get_coordenadas(request)
        return render_template("login.html")


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


@app.route("/registro", methods=["POST", "GET"])
def registro():
    if request.method == "POST":
        nombre = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if nombre == "" or email == "" or password == "":
            return render_template("registro.html")

        if registro_usuarios(nombre, email, password):
            mensaje = "Registered User"
            return render_template("registro.html", mensaje=mensaje)
        else:
            mensaje = "User already exists"
            return render_template("registro.html", mensaje=mensaje)
    else:
        return render_template("registro.html")


@app.route("/principal", methods=["POST", "GET"])
def principal():
    ubicacion_dict = get_coordenadas(request)
    coord = (
        str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude"))
    )
    city = PeticionCoordenadas(coord)
    # urls = get_imagen(city)
    # url = urls[0]
    return render_template("principal.html")


@app.route("/eventos")
def eventos():
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

    return render_template(
        "eventos.html", eventos=eventos, get_img=get_image, get_categ=get_categoria
    )  # Enviamos los datos que queremos mostrar en el html5 list es el atributo que queremos de la api


@app.route("/infoEvento")
def infoEventos():
    id_evento = request.args.get("id") #Obtenemos el id de cada evento
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&id=" + id_evento
    )
    datosFormatonJSON = datosObtenidos.json()
    info = datosFormatonJSON.get("_embedded")
    evento = info.get("events")[0]

    nombre = evento.get("name")
    # imagen = evento.get("images")[0].get("url")
    precioMin = 0
    precioMax = 0
    if evento.get("priceRanges") in evento:
        precioMin = evento.get("priceRanges")[0].get("min")
        precioMax = evento.get("priceRanges")[0].get("max")

    fecha = evento.get("dates").get("start").get("localDate")
    masInfo = info.get("_embedded")
    # ciudad = masInfo.get("venues")[0].get("city").get("name")
    # direccion = masInfo.get("address").get("line1")
    # venues = masInfo.get("venues")[0].get("name")

    print("Nombre: ",nombre)
    print("PrecioMin: ",precioMin)
    print("PrecioMax: ",precioMax)
    print("Fecha: ",fecha)
    # print("Ciudad: ",ciudad)
    # print("Direccion: ",direccion)
    # print("Venues: ",venues)

    return render_template("infoEvento.html")


@app.route("/eventosUbic", methods=["POST"])
def eventosPorUbicacion():
    city = request.form["search"]
    categoria = request.form["categorias"]
    datosObtenidos = ""

    if city != " " and categoria != "disabled selected":
        datosObtenidos = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json?classificationName="
            + categoria
            + "&city="
            + city
            + "&apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&language=es&countryCode=ES"
        )

    elif city != " " and categoria == "disabled selected":
        datosObtenidos = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json?&city="
            + city
            + "&apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&language=es&countryCode=ES"
        )

    elif city == " " and categoria != "disabled selected":
        datosObtenidos = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json?classificationName="
            + categoria
            + "&apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&language=es&countryCode=ES"
        )
    else:
        datosObtenidos = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json?apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&language=es&countryCode=ES"
        )
        datosFormatonJSON = datosObtenidos.json()
        if int(datosFormatonJSON.get("page").get("totalElements")) > 4:
            save_file_json_events(datosFormatonJSON)

    datosFormatonJSON = datosObtenidos.json()

    if (datosFormatonJSON.get("page").get("totalElements") == 0) or (
        int(datosFormatonJSON.get("page").get("totalElements")) <= 5
    ):
        datosFormatonJSON = load_file_json_events()

    info = datosFormatonJSON.get("_embedded")
    eventos = info.get("events")

    if len(eventos) == 0:
        return render_template("eventos.html")

    get_image = lambda event: event["images"][-1]
    get_categoria = lambda categ: categ["classifications"][0]["segment"]

    return render_template(
        "eventosUbic.html", eventos=eventos, get_img=get_image, get_categ=get_categoria
    )


@app.route("/noticias")
def Noticias():
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

    info = datosFormatonJSON.get("results")

    return render_template("noticias.html", noticias=info)


@app.route("/noticiasUbic", methods=["POST", "GET"])
def NoticiasPorUbic():
    city = request.form["search"]
    categoria = request.form["categorias"]

    if city != " " and categoria != "disabled selected":
        datosObtenidos = requests.get(
            "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news%20AND%20&country=es"
            + city
            + "&language=es&category="
            + categoria
        )

    elif city != " " and categoria == "disabled selected":
        datosObtenidos = requests.get(
            "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news%20AND%20&country=es"
            + city
            + "&language=es"
        )

    elif city == " " and categoria != "disabled selected":
        datosObtenidos = requests.get(
            "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news&language=es&country=es&category="
            + categoria
        )

    else:
        datosObtenidos = requests.get(
            "https://newsdata.io/api/1/news?apikey=pub_7421c00b07c3b0a1ab68df5be83ae037be9f&q=news&language=es&country=es"
        )
        datosFormatonJSON = datosObtenidos.json()
        if ("totalResults" in datosFormatonJSON) and int(
            datosFormatonJSON.get("totalResults")
        ) > 5:
            save_file_json_news(datosFormatonJSON)

    datosFormatonJSON = datosObtenidos.json()

    if (not "totalResults" in datosFormatonJSON) or int(
        datosFormatonJSON.get("totalResults")
    ) < 1:
        datosFormatonJSON = load_file_json_news()

    info = datosFormatonJSON.get("results")

    if len(info) == 0:
        return render_template("noticias.html")

    return render_template("noticiasUbic.html", noticias=info)


@app.route("/meterologiaUbic")
def meterologiaUbic():
    ubicacion_dict = get_coordenadas(request)
    coord = (
        str(ubicacion_dict.get("latitude")) + "," + str(ubicacion_dict.get("longitude"))
    )

    city = PeticionCoordenadas(coord)
    cont = 5

    while city == None and cont < 6:
        city = PeticionCoordenadas(coord)
        cont = cont - 1

    if city == None:
        mensaje = "Este Servicio no se encuentra disponible en este momento."
        return render_template("meterologiaUbicError.html",mensaje=mensaje)

    datosObtenidos = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q="
        + city
        + "&appid=8ca0c1c6f4748e36b8463b280a518364&units=Metric&lang=es"
    )

    datosFormatonJSON = datosObtenidos.json()
    if datosFormatonJSON.get("cod") == "404":
        mensaje = "Este Servicio no se encuentra disponible en este momento."
        return render_template("meterologiaUbicError.html",mensaje=mensaje)

    info = datosFormatonJSON.get("main")
    weather = datosFormatonJSON.get("weather")[0]
    today = date.today()
    fecha = today.strftime("%m-%d-%Y")

    meterologia = {
        "fecha": fecha,
        "city": city,
        "description": weather["description"],
        "clim": weather["main"],
        "icon": weather["icon"],
        "temp": round(info["temp"]),
        "temp_min": round(info["temp_min"]),
        "temp_max": round(info["temp_max"]),
        "pressure": info["pressure"],
        "humidity": info["pressure"],
        "windspeed": datosFormatonJSON["wind"]["speed"],
    }

    clima7d = climaDia(coord)

    if clima7d == None :
        mensaje = "La Previsión del Tiempo no está disponible en este momento."
        return render_template("meterologiaUbic.html",weather=meterologia,clima7d=[],preparase={},mensaje=mensaje)
    
    
    preparase = Preparese_Para_Su_Dia(city)

    return render_template(
        "meterologiaUbic.html",
        weather=meterologia,
        clima7d=clima7d,
        preparase=preparase,
    )


def get_coordenadas(request: Request):
    coordenadas = request.cookies.get("ubicacion")
    if coordenadas == None:
        return
    coordenadas = json.loads(coordenadas)
    return coordenadas


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
    mapa.save("templates/mapa.html")

    return render_template("mapa.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
