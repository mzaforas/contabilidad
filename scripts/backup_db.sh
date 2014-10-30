#!/bin/bash

NOW=$(date +"%Y-%m-%d_%H-%M")
cd /home/pi/contabilidad/db/
tar -cvzf /tmp/contabilidad_$NOW.db.tar.gz contabilidad.db
scp /tmp/contabilidad_$NOW.db.tar.gz pi@xbmc:/media/STOREX/Backup/contabilidad/