# Spark Execution

## Objetivo

Este documento explica cómo ejecutar la versión PySpark del proyecto usando Docker.

La versión Spark se agregó como una mejora técnica para preparar el pipeline hacia un escenario más escalable y cercano a nube. No reemplaza todavía al pipeline principal con pandas, sino que funciona como una implementación paralela para validar procesamiento con PySpark.

---

## Decisión técnica

Primero se intentó ejecutar PySpark directamente en Windows, pero Spark requiere configuración adicional para operaciones locales de escritura, como Java, Hadoop y `winutils.exe`.

Para evitar dependencias específicas de Windows, se decidió ejecutar PySpark dentro de Docker. Esto permite trabajar en un entorno Linux más reproducible y portable.

---

## Tecnología utilizada

- Docker
- Python 3.12
- Java 21
- PySpark 4.1.2

---

## Archivos relacionados

```text
docker/Dockerfile.spark
requirements-spark.txt
run_spark_pipeline.py
src/spark/spark_session.py
src/spark/spark_silver.py
src/spark/spark_gold.py