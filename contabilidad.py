# -*- coding: utf-8 -*-

# all the imports

import os
import os.path
import datetime
import time
import arrow

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import secure_filename
from excel_parser import parse_file
from model import init_db, connect_db, get_proveedores, get_movimientos, get_categorias, get_proveedor, get_categoria, update_proveedor, get_total_by_category


# app instance
app = Flask(__name__)

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
DATABASE = os.path.join(app.root_path, 'db/contabilidad.db')
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db_conn = connect_db(app)


@app.teardown_request
def teardown_request(exception):
    db_conn = getattr(g, 'db_conn', None)
    if db_conn is not None:
        db_conn.close()


def _calculo_importes_anuales(year, nombre_categorias, categoria_id=None):
    importe_categorias_mes = dict((id, dict()) for id in nombre_categorias.keys())
    total_yearly_by_categoria = dict((id, 0.0) for id in nombre_categorias.keys())
    total_yearly_by_categoria[0] = 0.0


    for month in range(1, 13):
        total_by_month = 0.0
        from_time = datetime.datetime(year, month, 1, 0, 0)
        if month == 12:
            to_time = datetime.datetime(year+1, 1, 1, 0, 0)
        else:
            to_time = datetime.datetime(year, month+1, 1, 0, 0)

        movimientos = get_total_by_category(g.db_conn, from_time, to_time, categoria_id)
        for movimiento_categoria_id, importe in movimientos:
            if movimiento_categoria_id is not None:
                importe_categorias_mes[movimiento_categoria_id][month] = importe
                total_by_month += importe
                total_yearly_by_categoria[movimiento_categoria_id] += importe

        # Total por mes
        importe_categorias_mes[0][month] = total_by_month
        total_yearly_by_categoria[0] += total_by_month
    # Total por categoria
    for total_categoria_id, total in total_yearly_by_categoria.iteritems():
        # 0 is used as key for full year
        importe_categorias_mes[total_categoria_id][0] = total
    return importe_categorias_mes


# controllers
@app.route('/', defaults={'year': None})
@app.route("/<int:year>")
def index(year):
    if year is None:
        year = arrow.now().year

    # Cálculo de importe categoría mes
    nombre_categorias = dict((id, nombre) for (id, nombre) in get_categorias(g.db_conn))
    nombre_categorias[0] = 'total'

    importe_categorias_mes = _calculo_importes_anuales(year, nombre_categorias)

    months = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre',
        0: u'total año'}

    # Cálculo de los proveedores pendientes de asignar categoría
    query = 'select count(*) from proveedores where categoria_id is null'
    proveedores_sin_categoria = get_proveedores(g.db_conn, query)[0][0]

    # Cálculo de la fecha del último movimiento
    query = 'select fecha from movimientos order by fecha desc limit 1'
    lista_movimientos = get_movimientos(g.db_conn, query)
    if not lista_movimientos:
        fecha_ultimo_movimiento = 0
    else:
        fecha_ultimo_movimiento = arrow.get(lista_movimientos[0][0]).format('DD/MM/YYYY')

    return render_template('index.html',
                           importe_categorias_mes=importe_categorias_mes,
                           months=months,
                           nombre_categorias=nombre_categorias,
                           proveedores_sin_categoria=proveedores_sin_categoria,
                           fecha_ultimo_movimiento=fecha_ultimo_movimiento,
                           year=year)


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['xls'])


@app.route("/proveedores")
def proveedores():
    proveedores = get_proveedores(g.db_conn)
    return render_template('proveedores.html', proveedores=proveedores)


@app.route("/proveedores-sin-categoria")
def proveedores_sin_categoria():
    query = 'select * from proveedores where categoria_id is null'
    proveedores = get_proveedores(g.db_conn, query)
    return render_template('proveedores.html', proveedores=proveedores)


@app.route("/movimientos")
def movimientos():
    movimientos = get_movimientos(g.db_conn)
    return render_template('movimientos.html', movimientos=movimientos)

@app.route('/grafica-categoria/<int:categoria_id>', defaults={'year': None})
@app.route("/grafica-categoria/<int:year>/<int:categoria_id>")
def grafica_categoria(year, categoria_id):
    if year is None:
        year = arrow.now().year

    importes_anuales = {0: 0.0}
    if categoria_id == 0:
        categoria = (0, 'Total')
    else:
        categoria = get_categoria(g.db_conn, categoria_id)
        importes_anuales.update({categoria_id: 0.0})
    importes = _calculo_importes_anuales(year, importes_anuales, categoria_id)
    return render_template('grafica_categoria.html', importes=importes[0], categoria=categoria)


@app.route("/detalle-movimientos/<int:year>/<int:month>/<int:categoria_id>")
def detalle_movimientos(year, month, categoria_id):

    from_time = datetime.datetime(year, month, 1, 0, 0)
    if month == 12:
        to_time = datetime.datetime(year + 1, 1, 1, 0, 0)
    else:
        to_time = datetime.datetime(year, month + 1, 1, 0, 0)

    if categoria_id == 0:
        query = 'select date(m.fecha, "unixepoch"), m.importe, p.nombre from movimientos m join proveedores p on m.proveedor_id=p.id where m.fecha>=%s and m.fecha<%s order by m.fecha;' % (from_time.strftime("%s"), to_time.strftime("%s"))
    else:
        query = 'select date(m.fecha, "unixepoch"), m.importe, p.nombre from movimientos m join proveedores p on m.proveedor_id=p.id where m.fecha>=%s and m.fecha<%s and p.categoria_id=%s order by m.fecha;' % (from_time.strftime("%s"), to_time.strftime("%s"), categoria_id)
    movimientos = get_movimientos(g.db_conn, query)

    print movimientos
    return render_template('movimientos.html', movimientos=movimientos)


@app.route("/upload", methods=['POST'])
def upload():
    fd = request.files['file']
    if not fd or not fd.filename:
        flash('Fichero vacio o no recibido')
    elif not _allowed_file(fd.filename):
        flash('Tipo de fichero (%s) no permitido' % fd.filename.rsplit('.', 1)[1])
    else:
        filename = secure_filename(fd.filename)
        fd.save(os.path.join('/tmp', filename))
        movimientos_leidos = parse_file(g.db_conn, '/tmp/%s' % filename)
        flash('El fichero ha sido procesado correctamente. Leidos %d movimientos' % movimientos_leidos)

    return redirect(url_for('index'))


@app.route("/asignar-categoria/<int:proveedor_id>", methods=['GET', 'POST'])
def asignar_categoria(proveedor_id):
    proveedor = get_proveedor(g.db_conn, proveedor_id)
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id')
        update_result = update_proveedor(g.db_conn, proveedor_id, 'categoria_id', categoria_id)
        categoria = get_categoria(g.db_conn, categoria_id)
        if update_result == 1:
            flash('Categoria "%s" asignada a proveedor' % categoria[1].capitalize())
        else:
           flash('Error asignando categoria "%s" a proveedor' % categoria[1].capitalize()) 
        return redirect(url_for('proveedores'))

    categorias = get_categorias(g.db_conn)
    return render_template('asignar_categoria.html', proveedor=proveedor, categorias=categorias)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
