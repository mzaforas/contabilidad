import xlrd
import datetime
import arrow

from model import insert_movimiento

def parse_file(db_conn, path):
    """
    parse excel file
    """
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_index(0)

    movimientos = [parse_row(db_conn, sheet.row(row_id)) for row_id in xrange(4, sheet.nrows)]

    return len(movimientos)
    
def parse_row(db_conn, row):
    """
    parse excel row
    """
    fecha = arrow.get(row[0].value, 'DD/MM/YYYY').datetime
    proveedor = row[1].value
    importe = row[2].value
    saldo = row[3].value
    
    return insert_movimiento(db_conn, fecha, proveedor, importe, saldo)

