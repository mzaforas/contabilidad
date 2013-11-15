import shutil
import datetime

date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
shutil.copy('/home/pi/raspberrypi/contabilidad/db/contabilidad.db', '/media/STOREX/Backup/contabilidad/contabilidad_{date}.db'.format(date=date))
