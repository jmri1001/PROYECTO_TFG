import folium
from folium.plugins import MiniMap


ubicaciones = {"Burgos":[40.463667,-3.74922],"Caceres":[39.47649,-6.37224]}

mapa = folium.Map(location=[40.463667,-3.74922],zoom_start=6.45, control_scale=True)   #Carga el mapa de Espana

for ubic in ubicaciones:
    ubicacion = "<b>"
    ubicacion += ubic
    ubicacion += "</b>"

    coordenadas = ubicaciones.get(ubic)

    #Ubicaciones de las cuales se muestran los eventos y noticias en el mapa
    folium.Marker(location=coordenadas,popup=ubicacion).add_to(mapa)
    #Colocamos el icono de ubicacion 
    folium.Circle(location=coordenadas,color="purple",fill_color="red",radius=50,weight=4,fill_opacity=0.5,tooltip=ubicacion).add_to(mapa) 


minimapa = MiniMap()
mapa.add_child(minimapa)

mapa.save('C:\\Users\\jose.LAPTOP-EQOVD9G7\\Desktop\\Apps\\DemoApis\\templates\\mapa.html')





