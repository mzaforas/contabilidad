import sqlite3
import os

# 2013-10-14
#categorias = ['agua', 'luz', 'gas', 'gasolina', 'alquiler', 'supermercado', 'casa', 'deporte', 'cine', 'amazon', 'movil', 'nomina', 'cajero', 'transporte', 'belleza', 'salud', 'viajes', 'ropa', 'internet', 'restaurantes', 'eventos']

# 2013-10-15
#categorias = ['boda', 'uned']

# 2013-10-16
#categorias = ['COIT', 'coche', 'regalos', 'renta']

# 2013-10-17
categorias = ['ingreso extra']

db_path = os.path.dirname(os.path.abspath(__file__)) + '/../db/contabilidad.db'
db_conn = sqlite3.connect(db_path)
cursor = db_conn.cursor()

for categoria in categorias:
    result = cursor.execute('insert into categorias (nombre) values (?)', (categoria,))
    print result

db_conn.commit()
db_conn.close()
