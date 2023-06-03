import json
import requests
import folium
from folium.plugins import MiniMap
from ..db import con
from ..utils import relative_to
from .FuncionesCompartidas import TiempoParaEventos


from src.db import *

def Evento_Favorito(
    nombre,
    PrecioMin,
    PrecioMax,
    fecha,
    ciudad,
    direccion,
    venues,
    imagen,
    latitud,
    longitud,
    usuario,
):
    # Añadimos a la base de datos el evento elegido por el usuario como favorito
    cur = con.cursor()
    cur.execute(
        "SELECT count(Nombre) FROM EventosFavoritos WHERE Nombre=? AND Ciudad=? AND IdUsuario=?",
        (
            nombre,
            ciudad,
            usuario,
        ),
    )
    resul = cur.fetchall()
    count = resul[0][0]

    if count == 0:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO EventosFavoritos(Nombre,PrecioMax,PrecioMin,Fecha,Ciudad,Direccion,Imagen,Venues,Latitud,Longitud,IdUsuario,Usuario) values (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                nombre,
                PrecioMax,
                PrecioMin,
                fecha,
                ciudad,
                direccion,
                imagen,
                venues,
                latitud,
                longitud,
                usuario,
                usuario,
            ),
        )
        result = cur.fetchone()
        con.commit()
        TiempoParaEventos(latitud, longitud, ciudad)
        return True
    
    con.commit()
    return False


def prevision_clima(city):
    datosObtenidos = requests.get(
        "http://api.openweathermap.org/data/2.5/forecast?q="
        + city
        + "&cnt=8&appid=8ca0c1c6f4748e36b8463b280a518364&units=Metric&lang=es"
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
        temp = str(round(temp)) + "ºC"
        descr = weather.get("weather")[0].get("description")
        date = weather.get("dt_txt")
        valor = date.split(" ", 1)
        hora = valor[1][:5]

        info = {
            "temp": temp,
            "icono": weather.get("weather")[0].get("icon"),
            "lluvia": weather.get("pop"),
            "fecha": hora,
            "descripcion": descr,
        }
        temperatura.append(temp)
        por_horas.append(hora)
        lista.append(info)

    return (temperatura, por_horas, lista)

def load_file_json_events():
    eventos_path = relative_to(__file__,"../eventos.json")
    with open(eventos_path, "r") as fp:
        data = json.load(fp)
        return data

def save_file_json_events(my_dict):
    eventos_path = relative_to(__file__,"../eventos.json")
    with open(eventos_path, "w") as fp:
        json.dump(my_dict, fp)


def Eventos(id):
    # Extraemos de la base de datos los eventos elegidos por el usuario como favoritos
    cur = con.cursor()
    cur.execute("SELECT * FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()
    con.commit()

    mapa = folium.Map(
        location=[40.463667, -3.74922], zoom_start=6.45, control_scale=True
    )  # Carga el mapa de Espana

    for tupla in resul:
        latitud = tupla[8]
        longitud = tupla[9]
        ubicacion = tupla[7]
        evento = "<b>Evento: "
        evento += tupla[0]
        evento += "</b>"

        # Ubicaciones de las cuales se muestran los eventos y noticias en el mapa
        folium.Marker(
            location=[latitud, longitud],
            popup=evento,
            icon=folium.Icon(color="lightgreen"),
        ).add_to(mapa)
        # Colocamos el icono de ubicacion
        folium.Circle(
            location=[latitud, longitud],
            color="purple",
            fill_color="red",
            radius=50,
            weight=4,
            fill_opacity=0.5,
            tooltip=ubicacion,
        ).add_to(mapa)

    minimapa = MiniMap()
    mapa.add_child(minimapa)

    mapa_path = relative_to(__file__,"../templates/mapa.html")

    mapa.save(mapa_path)


def Eventos_DB_Mapa(id):
    # Extraemos de la base de datos los eventos elegidos por el usuario como favoritos
    cur = con.cursor()
    cur.execute("SELECT * FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()
    con.commit()
    return resul


def BorrarEventoFav(nombre, ciudad):
    cur = con.cursor()
    cur.execute(
        "DELETE FROM EventosFavoritos WHERE Nombre=? AND Ciudad=?",
        (
            nombre,
            ciudad,
        ),
    )
    con.commit()


def infoEventosApi(idEvento):
    datosObtenidos = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json?apikey=FKM66NQuNZ4k6GAAEJWl57l2tYDQ7VTA&id="
        + idEvento
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

    infoEvento = {
        "nombre": nombre,
        "PrecioMin": precioMin,
        "PrecioMax": precioMax,
        "Fecha": fecha,
        "Ciudad": ciudad,
        "Direccion": direccion,
        "Venues": venues,
        "Imagen": imagen,
        "Latitud": latitud,
        "Longitud": longitud,
    }

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
    ubicacion = "España"
    categoria = "Todas"

    return (eventos, get_image, get_categoria, ubicacion, categoria)

def Ubicaciones(id):
    # Extraemos de la base de datos los eventos elegidos por el usuario como favoritos

    cur = con.cursor()
    cur.execute("SELECT DISTINCT Ciudad FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()

    lista = []
    url = "https://v5i.tutiempo.net"
    wd, wi = f"{url}/wd/big/black/", f"{url}/wi/"
    wi_icon = wi + "{style}/{size}/{icon}.png"
    wd_icon = wd + "{icon}.png"

    for tupla in resul:
        for ciudad in tupla:
            if ciudad == "Vitoria-Gasteiz":
                ciudad = "Vitoria"

            cur.execute("SELECT * FROM Ubicaciones WHERE Ciudad=?", (ciudad,))
            infocity = cur.fetchall()

            if len(infocity) > 0:
                info = {
                    "ciudad": infocity[0][0],
                    "fecha": infocity[0][1],
                    "temp_min": infocity[0][3],
                    "temp_max": infocity[0][2],
                    "icono": infocity[0][4],
                    "viento": infocity[0][5],
                    "icono_viento": infocity[0][6],
                    "wi_icon": wi_icon,
                    "wd_icon": wd_icon,
                }
                lista.append(info)

    con.commit()
    return lista