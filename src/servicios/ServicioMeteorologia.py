import requests
from ..db import con
from ..utils import relative_to
from datetime import date
from .ServicioEventos import prevision_clima
from .FuncionesCompartidas import TiempoParaEventos

def climaDia(coordenadas):
    if coordenadas == "42.3443701,-3.6927629" or coordenadas == "42.34995,-3.69205":
        coordenadas = "41.6704100,-3.6892000"

    datosObtenidos = requests.get(
        "https://api.tutiempo.net/json/?lan=es&&units=Metric&apid=XwY44q4zaqXbxnV&ll="
        + coordenadas
    )
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
            "wd_icon": wd_icon,
        }

        lista.append(info)

    return lista


def ActualizarTiempoEventos(id):
    cur = con.cursor()
    cur.execute("SELECT DISTINCT Ciudad FROM EventosFavoritos WHERE IdUsuario=?", (id,))
    resul = cur.fetchall()

    for tupla in resul:
        for ciudad in tupla:
            cur.execute(
                "SELECT Latitud,Longitud FROM Ubicaciones WHERE Ciudad=?", (ciudad,)
            )
            infocity = cur.fetchall()

            if len(infocity) > 0:
                latitud = infocity[0][0]
                longitud = infocity[0][1]
                TiempoParaEventos(latitud, longitud, ciudad)
    con.commit()


def Preparese_Para_Su_Dia(city):
    lista = prevision_clima("Burgos")
    datos = lista[2][0]
    info = {}

    today = date.today()
    fecha = today.strftime("%a, %d %b %Y")
    paraguas = "No es necesario"
    abrigo = "Ropa fina"
    sensacion_termica = datos.get("temp")
    al_aire_libre = datos.get("descripcion")
    temp = datos.get("temp")
    temp = temp.split("º", 1)

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
        "fecha": fecha,
    }

    return info