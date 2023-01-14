import requests

def PeticionCoordenadas(coordenadas):
        url = "http://geocode.xyz/"+coordenadas+"?json=1&region=ES"
        datosObtenidos = requests.get(url)
        datosFormatoJSON = datosObtenidos.json()

        if ( datosFormatoJSON == None or  datosFormatoJSON.get("error") != None): return None
        
        osmtags = datosFormatoJSON.get("osmtags")
        
        if(osmtags != "{}"): 
                
                return osmtags.get("name")
                
        else:
                return None
