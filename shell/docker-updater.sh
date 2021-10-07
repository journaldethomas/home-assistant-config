#!/bin/bash

cd /opt/docker/compose/homeassistant/
if [ -e "docker-compose.yml" ]
then
   /usr/local/bin/docker-compose pull homeassistant_prod && /usr/local/bin/docker-compose up -d
   echo "Home assistant mis à jour"
else
   echo "Aucune action effectuée"
fi

