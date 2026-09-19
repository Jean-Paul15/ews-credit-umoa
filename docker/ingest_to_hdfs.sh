#!/bin/sh
# Copie le flux d'evenements et les tables synthetiques (montes en lecture
# seule dans le namenode) vers HDFS. A executer apres
# `docker compose up -d namenode datanode`.
set -e

docker exec ews-namenode hdfs dfs -mkdir -p /events /synthetic
docker exec ews-namenode sh -c "hdfs dfs -put -f /staging/events/* /events/"
docker exec ews-namenode sh -c "hdfs dfs -put -f /staging/synthetic/clients.csv /staging/synthetic/credits.csv /staging/synthetic/labels.csv /synthetic/"

docker exec ews-namenode hdfs dfs -ls /events
docker exec ews-namenode hdfs dfs -ls /synthetic
