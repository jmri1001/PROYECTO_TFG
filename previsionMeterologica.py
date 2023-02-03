import requests
from datetime import datetime 
from deep_translator import GoogleTranslator
import pandas as pd
import numpy as np


#Funcion que devuelve el dia de la semana respecto a una fecha pasada como parametro
def Fecha_d(fecha):
    date_sr = str(pd.to_datetime(fecha))
    dt = datetime.fromisoformat(date_sr)
    dia_Semana = dt.strftime("%A")
    traductor = GoogleTranslator(source='en', target='es')
    resultado = traductor.translate(dia_Semana)
    return resultado


#Llamada de datos meterologicos para hacer un grafico por horas
def Prevision_Clima(city):

    datosObtenidos = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?q=" + city + "&cnt=8&appid=8ca0c1c6f4748e36b8463b280a518364&units=Metric&lang=es"
        )
    datosFormatonJSON = datosObtenidos.json()

    lista = []
    info = {}

    lista_weather = datosFormatonJSON.get("list")

    for weather in lista_weather:
        temp_min = weather.get("main").get("temp_min")
        temp_max = weather.get("main").get("temp_max")
        temp_min = round(temp_min)
        temp_max = round(temp_max)
        date = weather.get("dt_txt")
        fecha = Fecha_d(date)

        info = {
            "temp_min": temp_min,
            "temp_max": temp_max,
            "icono": weather.get("weather")[0].get("icon"),
            "lluvia": weather.get("pop"),
            "fecha":  date
        }

        lista.append(info)

    return lista


def climaDia(coordenadas):
    datosObtenidos = requests.get( "https://api.tutiempo.net/json/?lan=es&&units=Metric&apid=XwY44q4zaqXbxnV&ll=" + coordenadas)
    datosFormatonJSON = datosObtenidos.json()

    dias = []
    dias.append(datosFormatonJSON.get("day2"))
    dias.append(datosFormatonJSON.get("day3"))
    dias.append(datosFormatonJSON.get("day4"))
    dias.append(datosFormatonJSON.get("day5"))
    dias.append(datosFormatonJSON.get("day6"))
    dias.append(datosFormatonJSON.get("day7"))

    lista = []

    for d in dias:
        date = d.get("date")
        temp_min = d.get("temperature_min")
        temp_max = d.get("temperature_max")
        icono = d.get("icon")
        viento = d.get("wind")
        icono_viento = d.get("icon_wind")
        date = Fecha_d(date)

        info = {
                "fecha": date,
                "temp_min": temp_min,
                "temp_max": temp_max,
                "icono": icono,
                "viento": viento,
                "icono_viento": icono_viento
            }

        lista.append(info)

    return lista

