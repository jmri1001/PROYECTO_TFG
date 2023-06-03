import requests
from ..db import con

def TiempoParaEventos(latitud, longitud, ciudad):
    cur = con.cursor()
    cur.execute("SELECT count(Ciudad) FROM Ubicaciones WHERE Ciudad=?", (ciudad,))
    resul = cur.fetchall()
    count = resul[0][0]

    if latitud != None and longitud != None:
        coordenadas = latitud + "," + longitud
        if coordenadas == "42.3443701,-3.6927629" or coordenadas == "42.34995,-3.69205":
            coordenadas = "41.6704100,-3.6892000"

        datosObtenidos = requests.get(
            "https://api.tutiempo.net/json/?lan=es&&units=Metric&apid=XwY44q4zaqXbxnV&ll="
            + coordenadas
        )
        datosFormatonJSON = datosObtenidos.json()
        dias = []
        dias.append(datosFormatonJSON.get("day1"))
        if None in dias:
            return None

        fecha = dias[0].get("date")
        TempMin = dias[0].get("temperature_min")
        TempMax = dias[0].get("temperature_max")
        icono = dias[0].get("icon")
        viento = dias[0].get("wind")
        iconoViento = dias[0].get("icon_wind")

        if count == 0:
            cur.execute(
                "INSERT INTO Ubicaciones(Ciudad,Fecha,TempMax,TempMin,Icono,Viento,IconoViento,Latitud,Longitud) values (?,?,?,?,?,?,?,?,?)",
                (
                    ciudad,
                    fecha,
                    TempMax,
                    TempMin,
                    icono,
                    viento,
                    iconoViento,
                    latitud,
                    longitud,
                ),
            )
            result = cur.fetchone()
            con.commit()
            return True

        else:
            cur.execute(
                "UPDATE Ubicaciones SET Fecha=?,TempMax=?,TempMin=?,Icono=?,Viento=?,IconoViento=? WHERE Ciudad=?",
                (fecha, TempMax, TempMin, icono, viento, iconoViento, ciudad),
            )
            result = cur.fetchone()
            con.commit()
            
            return True
        
    con.commit()
    return False