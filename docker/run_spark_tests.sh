#!/bin/sh
# Execute les tests du job de feature engineering DANS l'image Spark du
# projet (memes versions Java/Python que l'execution reelle) — rien n'est
# installe sur la machine hote au-dela de Docker lui-meme.
set -e

docker build -t ews-spark-test -f docker/spark/Dockerfile docker/spark

docker run --rm \
  -v "$(pwd)/src:/opt/spark/work-dir/src:ro" \
  -v "$(pwd)/tests:/opt/spark/work-dir/tests:ro" \
  -w /opt/spark/work-dir \
  ews-spark-test \
  python3 -m pytest tests/spark_jobs -q
