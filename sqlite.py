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
    sql="CREATE TABLE Usuarios( nombre Varchar(50) NOT NULL, email Varchar(50) PRIMARY KEY, password Varchar(30) NOT NULL, gustos Varchar(10), foto BLOB);"
    c.execute(sql)

    sql= "DROP TABLE IF EXISTS Gustos;"
    c.execute(sql)
    sql="CREATE TABLE Gustos( id INTEGER(5) NOT NULL, nombre Varchar(50) PRIMARY KEY);"
    c.execute(sql)

    sql= "DROP TABLE IF EXISTS UbicacionesFavoritas;"
    c.execute(sql)
    sql="CREATE TABLE UbicacionesFavoritas( nombre Varchar(50) PRIMARY KEY, fecha Varchar(20));"
    c.execute(sql)
    
    conn = conx[0]
    conn.close()

#crearDB()

email = 'pepe@email.com'

con = sqlite3.connect('DB.db')
cur = con.cursor()
cur.execute('SELECT count(email) FROM Usuarios WHERE email=?',(email))
resul = cur.fetchall()
count = resul[0][0]
print(count)