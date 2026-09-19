# Image Spark officielle Apache : Java et Python deja compatibles entre eux
# (contrairement a un poste de dev avec un JDK/Python recents) — on y ajoute
# seulement pytest pour executer les tests du job de feature engineering
# dans les memes conditions que l'execution reelle.
FROM apache/spark:3.5.9-python3

USER root
RUN pip install --no-cache-dir pytest==8.3.3
RUN mkdir -p /opt/spark/work-dir && chown spark:spark /opt/spark/work-dir
USER spark

# pyspark n'est pas installe via pip dans cette image officielle : le module
# est fourni en zip a cote des jars Spark, normalement ajoute au PYTHONPATH
# par les scripts spark-submit/pyspark — on l'expose aussi pour un `python3`
# direct (utile pour les tests, qui n'ont pas besoin d'un cluster). Le code
# du projet (monte en volume sur work-dir/src) y est ajoute une fois pour
# toutes pour ne pas avoir a recomposer PYTHONPATH a chaque `docker run`.
ENV PYTHONPATH="/opt/spark/work-dir/src:/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip"

WORKDIR /opt/spark/work-dir
