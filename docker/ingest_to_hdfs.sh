#!/bin/sh
# Copie le flux d'evenements local (monte en lecture seule dans le namenode)
# vers HDFS. A executer apres `docker compose up -d namenode datanode`.
set -e

docker exec ews-namenode hdfs dfs -mkdir -p /events
docker exec ews-namenode hdfs dfs -put -f /staging/events/* /events/
docker exec ews-namenode hdfs dfs -ls /events
