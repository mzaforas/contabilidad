#!/bin/bash

NOW=$(date +"%Y-%m-%d_%H-%M")
tar -cvzf /tmp/contabilidad_$NOW.db.tar.gz /home/pi/contabilidad/db/contabilidad.db
scp /tmp/contabilidad_$NOW.db.tar.gz pi@192.168.1.11:/media/STOREX/Backup/contabilidad/