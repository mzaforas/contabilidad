import sqlite3
import time

from contextlib import closing


# DB auxiliar functions
def connect_db(app):
    return sqlite3.connect(app.config['DATABASE'])


def init_db(app):
    with closing(connect_db(app)) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def insert_movimiento(db_conn, fecha, proveedor, importe, saldo):
    """
    insert one movimiento in DB
    """
    cursor = db_conn.cursor()

    # get or insert proveedor
    cursor.execute('select id from proveedores where nombre=?', (proveedor,))
    proveedor_object = cursor.fetchone()
    proveedor_id = proveedor_object[0] if proveedor_object else None
    
    if proveedor_id is None:
        cursor.execute('insert into proveedores (nombre) values (?)', (proveedor,))
        db_conn.commit()
        proveedor_id = cursor.lastrowid
        new_proveedor = True
    else:
        new_proveedor = False

    # insert movimiento if not exists
    movimiento_values = (proveedor_id, time.mktime(fecha.timetuple()), importe, saldo)
    cursor.execute('select id from movimientos where proveedor_id=? and fecha=? and importe=? and saldo=?', movimiento_values)
    movimiento = cursor.fetchone()
    if movimiento is None:
        cursor.execute('insert into movimientos (proveedor_id, fecha, importe, saldo) values (?,?,?,?)', movimiento_values)
        db_conn.commit()
        new_movimiento = True
    else:
        new_movimiento = False

    return new_proveedor, new_movimiento


def get_movimientos(db_conn, query=None):
    cursor = db_conn.cursor()
    if query is not None:
        cursor.execute(query)
    else:
        cursor.execute('select * from movimientos')
    return cursor.fetchall()


def get_movimientos_by_category(db_conn, from_time, to_time, category_id=None):
    if category_id:
        query = 'select p.categoria_id, sum(m.importe) from movimientos m join proveedores p on m.proveedor_id=p.id where m.fecha>=%s and m.fecha<%s and p.categoria_id=%s group by p.categoria_id;' % (from_time.strftime("%s"), to_time.strftime("%s"), category_id)
    else:
        query = 'select p.categoria_id, sum(m.importe) from movimientos m join proveedores p on m.proveedor_id=p.id where m.fecha>=%s and m.fecha<%s group by p.categoria_id;' % (from_time.strftime("%s"), to_time.strftime("%s"))

    cursor = db_conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def get_proveedores(db_conn, query=None):
    cursor = db_conn.cursor()
    if query is not None:
        cursor.execute(query)
    else:
        cursor.execute('select * from proveedores p left outer join categorias c on p.categoria_id=c.id')
    return cursor.fetchall()


def get_categorias(db_conn):
    cursor = db_conn.cursor()

    cursor.execute('select * from categorias order by nombre')
    return cursor.fetchall()


def get_proveedor(db_conn, proveedor_id):
    cursor = db_conn.cursor()

    cursor.execute('select * from proveedores where id=?', (proveedor_id,))
    return cursor.fetchone()


def get_categoria(db_conn, categoria_id):
    cursor = db_conn.cursor()

    cursor.execute('select * from categorias where id=?', (categoria_id,))
    return cursor.fetchone()


def update_proveedor(db_conn, proveedor_id, update_key, update_data):
    cursor = db_conn.cursor()

    cursor.execute('update proveedores set %s=? where id=?' % update_key, (update_data, proveedor_id))
    db_conn.commit()
    return cursor.rowcount
