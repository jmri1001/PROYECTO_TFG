import sqlite3

#Creamos las tablas de la base de datos

def conection_DB():
    conn = sqlite3.connect('DB.db')
    return (conn,conn.cursor())


def crearDB():
    conx = conection_DB()
    c = conx[1]

    #Create tables
    sql= "DROP TABLE IF EXISTS Usuarios;"
    c.execute(sql)
    sql="CREATE TABLE Usuarios( user Varchar(50) PRIMARY KEY, password Varchar(30) NOT NULL);"
    c.execute(sql)


    sql= "DROP TABLE IF EXISTS UbicacionesFavoritas;"
    c.execute(sql)
    sql="CREATE TABLE UbicacionesFavoritas( nombre Varchar(50) PRIMARY KEY, fecha Varchar(20));"
    c.execute(sql)
    
    conn = conx[0]
    conn.close()

crearDB()
