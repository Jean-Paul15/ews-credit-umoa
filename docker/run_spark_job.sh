#!/bin/sh
# Lance le job de feature engineering distribue sur le cluster Spark/HDFS.
# A executer apres docker/ingest_to_hdfs.sh.
set -e

docker exec ews-spark-master spark-submit \
  --master spark://spark-master:7077 \
  /opt/bitnami/spark/work-dir/src/ews_credit/spark_jobs/run_feature_pipeline.py \
  --entree hdfs://namenode:9000/events \
  --sortie hdfs://namenode:9000/features
