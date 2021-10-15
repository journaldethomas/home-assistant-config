#!/bin/bash
LOG_FILE=/opt/doker/compose/homessistant/update.log

cd /opt/docker/compose/homeassistant/
touch $LOG_FILE
if [ -e "docker-compose.yml" ]
then
   echo "Début de la mise à jour" > $LOG_FILE
   /usr/local/bin/docker-compose pull homeassistant_prod && /usr/local/bin/docker-compose up -d
   echo "Home assistant a été mis à jour" > $LOG_FILE
else
   echo "Aucune action effectuée" > $LOG_FILE
fi

