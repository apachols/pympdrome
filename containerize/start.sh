#!/bin/sh

docker-compose stop $1 && docker-compose rm -f $1 && docker-compose up -d $1 && docker-compose logs $1;

sleep 1;

CONTAINER_ID=$(docker ps -aqf "name=pympdrome_$1_1")

docker exec -it $CONTAINER_ID mpd

sleep 1;

docker exec -it -e FLASK_DEBUG=1 $CONTAINER_ID python /home/server.py $2;
