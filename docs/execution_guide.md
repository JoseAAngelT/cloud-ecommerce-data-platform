# Execution Guide

## Objetivo

Esta guía explica cómo ejecutar el proyecto de forma local, desde la preparación del entorno hasta la carga de las tablas Gold en PostgreSQL.

---

## Requisitos previos

Antes de ejecutar el proyecto, se necesita tener instalado:

* Python 3.13
* Git
* PostgreSQL
* Power BI Desktop
* VS Code o un editor similar

También se recomienda tener pgAdmin 4 para revisar las tablas cargadas en PostgreSQL.

---

## 1. Clonar el repositorio

```powershell
git clone https://github.com/JoseAAngelT/cloud-ecommerce-data-platform.git
cd cloud-ecommerce-data-platform
```

---

## 2. Crear entorno virtual

```powershell
python -m venv .venv
```

Activar el entorno virtual en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## 4. Agregar archivos fuente

Descargar el dataset de Olist Brazilian E-Commerce y colocar los archivos CSV en:

```text
data/landing/
```

Archivos esperados:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

---

## 5. Crear base de datos en PostgreSQL

Crear una base de datos llamada:

```text
ecommerce_dw
```

Desde pgAdmin 4 se puede ejecutar:

```sql
CREATE DATABASE ecommerce_dw;
```

Si se usa `psql`, el comando puede variar según la instalación de PostgreSQL.

Ejemplo con ruta completa en Windows:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE DATABASE ecommerce_dw;"
```

---

## 6. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Ejemplo:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

El archivo `.env` no debe subirse al repositorio.

---

## 7. Revisar configuración del proyecto

La configuración principal se encuentra en:

```text
config/config.yaml
```

Este archivo contiene rutas del proyecto, nombres de archivos fuente, esquema de PostgreSQL y tablas Gold a cargar.

---

## 8. Ejecutar el pipeline

Desde la raíz del proyecto:

```powershell
python main.py
```

El pipeline ejecuta los siguientes pasos:

1. Ingesta de CSV a Bronze.
2. Transformaciones Silver.
3. Construcción de Gold.
4. Validaciones básicas de calidad.
5. Validaciones con Great Expectations.
6. Generación de reporte de ejecución.
7. Carga de tablas Gold a PostgreSQL.

---

## 9. Salida esperada

Durante la ejecución se deben mostrar mensajes similares a:

```text
Iniciando ingesta Bronze...
Transformaciones Silver finalizadas correctamente.
Transformaciones Gold finalizadas correctamente.
Validaciones basicas finalizadas | correctas: 47 | fallidas: 0
Validaciones GX finalizadas | correctas: 27 | fallidas: 0
Reporte de ejecucion generado: outputs\reports\execution_report.json
Carga de Gold a PostgreSQL finalizada correctamente.
Pipeline finalizado correctamente.
```

---

## 10. Revisar archivos generados

Después de ejecutar el pipeline, se generan archivos en:

```text
data/bronze/
data/silver/
data/gold/
outputs/quality/
outputs/reports/
```

Los datos procesados se guardan localmente y no se suben al repositorio.

---

## 11. Validar carga en PostgreSQL

En pgAdmin 4, conectarse a la base:

```text
ecommerce_dw
```

Revisar que exista el esquema:

```text
ecommerce_gold
```

Consulta para listar tablas:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'ecommerce_gold'
ORDER BY table_name;
```

Consulta de prueba:

```sql
SELECT *
FROM ecommerce_gold.agg_sales_by_month
ORDER BY year_month;
```

Otra consulta útil:

```sql
SELECT product_category_name_english, total_sales
FROM ecommerce_gold.agg_sales_by_category
ORDER BY total_sales DESC
LIMIT 10;
```

---

## 12. Ejecutar consultas de negocio

Las consultas analíticas se encuentran en:

```text
docs/business_queries.sql
```

Estas consultas pueden ejecutarse desde pgAdmin 4 o desde otro cliente SQL conectado a PostgreSQL.

---

## 13. Abrir dashboard en Power BI

El dashboard se encuentra en:

```text
dashboards/powerbi/ecommerce_dashboard.pbix
```

Power BI se conecta a PostgreSQL usando:

```text
Servidor: localhost
Base de datos: ecommerce_dw
```

El dashboard contiene cuatro páginas:

1. Resumen Ejecutivo.
2. Análisis de ventas.
3. Desempeño logístico.
4. Satisfacción del cliente.

---

## 14. Ejecutar Ruff

Para revisar formato y estilo del código:

```powershell
ruff check .
```

Para aplicar correcciones automáticas:

```powershell
ruff check . --fix
```

Para formatear código:

```powershell
ruff format .
```

---

## Problemas comunes

### PowerShell no permite activar el entorno virtual

Ejecutar PowerShell como administrador y usar:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Después volver a activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### `psql` no se reconoce como comando

Esto significa que PostgreSQL no está agregado al PATH de Windows.

Se puede usar la ruta completa:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432
```

La versión puede cambiar según la instalación local.

---

### Faltan variables de entorno

Si aparece un error indicando variables faltantes, revisar que el archivo `.env` exista en la raíz del proyecto y que use los nombres correctos:

```env
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

---

### Error de conexión a PostgreSQL

Revisar:

* Que PostgreSQL esté corriendo.
* Que la base `ecommerce_dw` exista.
* Que el usuario y contraseña sean correctos.
* Que el puerto sea `5432`.
* Que el archivo `.env` esté correctamente configurado.

---

## Resultado esperado

Al finalizar, el proyecto debe tener:

* Capas Bronze, Silver y Gold generadas.
* Validaciones de calidad ejecutadas.
* Reportes JSON generados.
* Tablas Gold cargadas en PostgreSQL.
* Dashboard de Power BI conectado a los datos procesados.
