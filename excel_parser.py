import xlrd
import datetime

from model import insert_movimiento

def parse_file(db_conn, path):
    """
    parse excel file
    """
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_index(0)

    movimientos = [parse_row(db_conn, sheet.row(row_id)) for row_id in xrange(5, sheet.nrows)]

    return len(movimientos)
    
def parse_row(db_conn, row):
    """
    parse excel row
    """
    fecha = datetime.datetime(*xlrd.xldate_as_tuple(row[1].value, 0))    
    proveedor = row[2].value
    importe = row[3].value
    saldo = row[4].value
    
    return insert_movimiento(db_conn, fecha, proveedor, importe, saldo)

