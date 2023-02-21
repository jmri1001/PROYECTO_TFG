import requests

def PeticionCoordenadas(coordenadas):
        url = "http://geocode.xyz/"+coordenadas+"?json=1&region=ES&auth=866831157714569401247x21047"
        datosObtenidos = requests.get(url)
        datosFormatoJSON = datosObtenidos.json()

        if ( datosFormatoJSON == None or  datosFormatoJSON.get("error") != None): return None
        
        osmtags = datosFormatoJSON.get("osmtags")
        
        if(osmtags != "{}"): 
                
                return osmtags.get("name")
                
        else:
                return None

def PeticionToponimo(city):
        url = "http://geocode.xyz/"+city+"?json=1&region=ES&auth=866831157714569401247x21047"
        datosObtenidos = requests.get(url)
        datosFormatoJSON = datosObtenidos.json()

        if ( datosFormatoJSON == None or  datosFormatoJSON.get("error") != None): return None
        
        latitud = datosFormatoJSON.get("latt")
        longitud = datosFormatoJSON.get("longt")
        coord = latitud + "," + longitud
        
        if(latitud != "0.00000" and longitud != "0.00000" ): 
                
                return coord
                
        else:
                return None
        
