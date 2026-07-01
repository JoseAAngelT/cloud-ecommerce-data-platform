# Cloud E-Commerce Data Platform

## Descripción

Este proyecto implementa un pipeline de datos para procesar información de e-commerce usando una arquitectura por capas: Bronze, Silver y Gold.

El objetivo es tomar datos transaccionales desde archivos CSV, limpiarlos, transformarlos y dejarlos listos para análisis en PostgreSQL y Power BI. El proyecto busca cubrir tanto la parte de ingeniería de datos como la parte analítica, conectando el procesamiento del dato con indicadores de negocio.

La primera versión está desarrollada de forma local, con una estructura preparada para evolucionar después hacia una implementación en nube.

---

## Caso de negocio

Una empresa de e-commerce necesita integrar información de órdenes, clientes, productos, vendedores, pagos, entregas y reseñas para analizar su operación.

Los datos originales se encuentran separados en diferentes archivos, por lo que se construyó un pipeline que permite organizarlos, transformarlos y generar salidas útiles para análisis de ventas, logística y satisfacción del cliente.

---

## Dataset

Se utiliza el dataset público **Olist Brazilian E-Commerce**, que contiene información histórica de órdenes realizadas en una plataforma de e-commerce.

El dataset incluye tablas relacionadas con:

- Clientes.
- Órdenes.
- Productos.
- Vendedores.
- Pagos.
- Reseñas.
- Entregas.
- Geolocalización.
- Traducción de categorías.

Los archivos originales se colocan en la carpeta:

```text
data/landing/
```

Los datos no se incluyen en el repositorio para evitar subir archivos pesados o generados localmente.

---

## Objetivo técnico

Construir un flujo de datos que permita:

- Ingestar archivos CSV.
- Guardar datos crudos en capa Bronze.
- Limpiar y estandarizar datos en capa Silver.
- Crear tablas analíticas en capa Gold.
- Ejecutar validaciones de calidad.
- Generar un reporte de ejecución.
- Cargar las tablas Gold a PostgreSQL.
- Construir un dashboard en Power BI.
- Agregar una versión paralela con PySpark.
- Dejar documentada una ruta de implementación en Azure.

---

## Arquitectura del pipeline

El flujo principal del proyecto es:

```text
CSV originales
    ↓
Landing
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Validaciones de calidad
    ↓
Reporte de ejecución
    ↓
PostgreSQL
    ↓
Power BI
```

La versión Spark funciona como flujo paralelo:

```text
Bronze
    ↓
Spark Silver
    ↓
Spark Gold inicial
```

---

## Capas de datos

### Bronze

La capa Bronze conserva una versión cercana a los datos originales.

En esta etapa se leen los archivos CSV desde `data/landing/` y se guardan en formato Parquet en `data/bronze/`.

También se agregan columnas técnicas de trazabilidad, como fecha de ingesta y archivo fuente.

### Silver

La capa Silver contiene datos limpios y estandarizados.

En esta etapa se realizan tareas como:

- Conversión de fechas.
- Conversión de columnas numéricas.
- Normalización de texto.
- Eliminación de duplicados.
- Estandarización de estados y categorías.
- Unión de productos con la traducción de categorías.

### Gold

La capa Gold contiene tablas listas para análisis.

Se construyeron dimensiones, hechos y tablas agregadas.

Dimensiones:

- `dim_customers`
- `dim_products`
- `dim_sellers`
- `dim_date`

Hechos:

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`
- `fact_delivery`

Agregados de negocio:

- `agg_sales_by_month`
- `agg_sales_by_category`
- `agg_delivery_performance`
- `agg_seller_performance`
- `agg_customer_satisfaction`

---

## Calidad de datos

Después de generar la capa Gold se ejecutan validaciones de calidad.

Se implementaron dos tipos de validaciones:

### Validaciones propias en Python

Estas validaciones revisan:

- Existencia de tablas.
- Tablas no vacías.
- Columnas obligatorias.
- Nulos en campos críticos.
- Valores negativos en montos.
- Rangos válidos, como calificaciones entre 1 y 5.

### Validaciones con Great Expectations

También se incorporó Great Expectations para definir reglas más formales sobre las tablas analíticas.

Algunas validaciones aplicadas son:

- `order_id` no debe ser nulo.
- `payment_value` debe ser mayor o igual a 0.
- `review_score` debe estar entre 1 y 5.
- `order_status` debe pertenecer a valores esperados.
- Las tablas principales deben tener registros.

Los reportes de calidad se generan en:

```text
outputs/quality/
```

---

## Reporte de ejecución

El pipeline genera un reporte general con el resumen de la ejecución.

El reporte incluye:

- Fecha de ejecución.
- Tablas procesadas por capa.
- Registros generados por tabla.
- Resultado de validaciones básicas.
- Resultado de validaciones con Great Expectations.
- Estado final del pipeline.

El archivo se genera en:

```text
outputs/reports/execution_report.json
```

---

## Carga a PostgreSQL

Las tablas Gold se cargan a PostgreSQL en el esquema:

```text
ecommerce_gold
```

Esta capa permite consultar los datos con SQL y conectar Power BI a una fuente estructurada.

Las credenciales se manejan con variables de entorno en un archivo `.env`, el cual no se sube al repositorio.

Ejemplo de configuración local:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

---

## Análisis de negocio

Se documentaron consultas SQL para revisar indicadores principales del negocio.

El archivo se encuentra en:

```text
docs/business_queries.sql
```

Algunos análisis incluidos son:

- Ventas mensuales.
- Top categorías por ventas.
- Top vendedores.
- Métodos de pago.
- Ventas por estado.
- Desempeño de entregas.
- Relación entre entrega tardía y calificación.
- Categorías con menor satisfacción.

También se documentaron los KPIs principales en:

```text
docs/business_kpis.md
```

---

## Dashboard en Power BI

Se construyó un dashboard en Power BI conectado a PostgreSQL.

El archivo del dashboard se encuentra en:

```text
dashboards/powerbi/ecommerce_dashboard.pbix
```

El dashboard incluye cuatro páginas:

### 1. Resumen Ejecutivo

Muestra los principales indicadores del negocio:

- Ventas totales.
- Órdenes totales.
- Ticket promedio.
- Calificación promedio.
- Tasa de entregas tardías.
- Ventas mensuales.
- Top categorías por ventas.

### 2. Análisis de ventas

Permite revisar el comportamiento comercial:

- Evolución mensual de ventas.
- Top categorías.
- Top vendedores.
- Valor pagado por método de pago.
- Detalle de vendedores.

### 3. Desempeño logístico

Permite analizar el comportamiento de entregas:

- Días promedio de entrega.
- Entregas totales.
- Entregas tardías.
- Tasa de entregas tardías.
- Entregas a tiempo vs tardías.
- Detalle mensual de entregas.

### 4. Satisfacción del cliente

Permite analizar la experiencia del cliente:

- Calificación promedio.
- Reseñas totales.
- Reseñas bajas.
- Reseñas altas.
- Calificación por mes.
- Categorías con menor satisfacción.
- Relación entre entrega tardía y calificación.

El diseño del dashboard está documentado en:

```text
docs/dashboard_design.md
```

---

## PySpark con Docker

Además del pipeline principal con pandas, se agregó una versión paralela con PySpark para preparar el proyecto hacia un escenario más escalable.

La ejecución de PySpark se realiza dentro de Docker para evitar dependencias específicas de Windows, como `winutils.exe`, `HADOOP_HOME` o configuraciones locales de Hadoop.

La versión Spark actual incluye:

- Transformaciones Silver para órdenes, clientes, artículos de orden, pagos, reseñas, productos y vendedores.
- Una primera versión Gold con dimensiones y una tabla de hechos de órdenes.
- Ejecución mediante un contenedor Docker.

Archivo principal de ejecución:

```text
run_spark_pipeline.py
```

Documentación relacionada:

```text
docs/spark_execution.md
```

Para ejecutar la versión Spark:

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  -w /app `
  cloud-ecommerce-spark `
  python run_spark_pipeline.py
```

---

## Arquitectura Azure y Terraform

El proyecto incluye una propuesta de arquitectura cloud en Azure.

La arquitectura considera servicios como:

- Azure Data Lake Storage Gen2.
- Azure Data Factory.
- Azure Databricks o Spark.
- Azure SQL Database.
- Azure Key Vault.
- Power BI.

La documentación se encuentra en:

```text
docs/azure_architecture.md
```

También se agregó una base de infraestructura como código con Terraform en:

```text
infra/terraform/
```

Esta base define recursos como:

- Resource Group.
- Storage Account con Data Lake Gen2.
- Contenedores para Landing, Bronze, Silver y Gold.
- Azure Key Vault.
- Azure SQL Database.
- Azure Data Factory.

La configuración fue validada con:

```powershell
terraform init
terraform validate
```

No se ejecutó `terraform apply`, ya que el objetivo por ahora es dejar la infraestructura definida sin crear recursos reales ni generar costos.

---

## Tecnologías utilizadas

- Python
- Pandas
- PySpark
- Docker
- PyArrow
- Parquet
- PostgreSQL
- SQLAlchemy
- Great Expectations
- Power BI
- Terraform
- Azure, como arquitectura propuesta
- Ruff
- Git y GitHub

---

## Estructura del proyecto

```text
cloud-ecommerce-data-platform/
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── landing/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── spark/
│
├── dashboards/
│   └── powerbi/
│
├── docker/
│   └── Dockerfile.spark
│
├── docs/
│   ├── architecture.md
│   ├── azure_architecture.md
│   ├── business_kpis.md
│   ├── business_queries.sql
│   ├── dashboard_design.md
│   ├── data_dictionary.md
│   ├── execution_guide.md
│   └── spark_execution.md
│
├── infra/
│   └── terraform/
│
├── outputs/
│   ├── quality/
│   └── reports/
│
├── src/
│   ├── ingest/
│   ├── load/
│   ├── quality/
│   ├── spark/
│   ├── transform/
│   └── utils/
│
├── main.py
├── run_spark_pipeline.py
├── requirements.txt
├── requirements-spark.txt
├── pyproject.toml
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Ejecución del proyecto

### 1. Crear entorno virtual

```powershell
python -m venv .venv
```

### 2. Activar entorno virtual en Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Colocar archivos fuente

Colocar los CSV originales del dataset en:

```text
data/landing/
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las credenciales de PostgreSQL.

Ejemplo:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

### 6. Ejecutar pipeline principal

```powershell
python main.py
```

---

## Flujo ejecutado por `main.py`

El archivo `main.py` ejecuta el pipeline principal en este orden:

1. Ingesta a Bronze.
2. Transformaciones Silver.
3. Construcción de Gold.
4. Validaciones básicas de calidad.
5. Validaciones con Great Expectations.
6. Generación de reporte de ejecución.
7. Carga de Gold a PostgreSQL.

La versión principal del pipeline se ejecuta con `main.py`.

La versión PySpark se ejecuta por separado con:

```text
run_spark_pipeline.py
```

Esto permite mantener estable el flujo principal y, al mismo tiempo, mostrar una alternativa más escalable con Spark.

---

## Ejecución con Docker y PySpark

Construir la imagen Docker:

```powershell
docker build -f docker/Dockerfile.spark -t cloud-ecommerce-spark .
```

Ejecutar pipeline Spark:

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  -w /app `
  cloud-ecommerce-spark `
  python run_spark_pipeline.py
```

La versión Spark genera salidas en:

```text
data/spark/silver/
data/spark/gold/
```

Estas salidas no se suben al repositorio.

---

## Terraform

La base de infraestructura se encuentra en:

```text
infra/terraform/
```

Comandos usados para validar:

```powershell
terraform init
terraform validate
```

No se requiere ejecutar Terraform para usar la versión local del proyecto.

---

## Convenciones de desarrollo

El proyecto utiliza Ruff para mantener un estilo de código consistente.

Comandos principales:

```powershell
ruff check .
ruff check . --fix
ruff format .
```

---

## Estado actual

Versión local funcional con extensión técnica hacia Spark y nube.

Actualmente el proyecto permite:

- Ejecutar el pipeline principal completo.
- Validar datos con reglas propias y Great Expectations.
- Cargar resultados a PostgreSQL.
- Analizar información en Power BI.
- Ejecutar una versión paralela con PySpark dentro de Docker.
- Mantener una propuesta de arquitectura Azure.
- Validar una base de infraestructura con Terraform.

---

## Próximos pasos

Como mejora futura, se considera:

- Ampliar Gold con PySpark para cubrir más tablas de hechos y agregados.
- Evaluar la carga de salidas Spark hacia PostgreSQL o Azure SQL.
- Ejecutar un despliegue controlado en Azure usando Terraform.
- Orquestar el flujo cloud con Azure Data Factory.
- Incorporar Key Vault para manejo de secretos en nube.
- Agregar monitoreo y alertas de ejecución.

Estas mejoras no reemplazan la versión local, sino que buscan evolucionar el proyecto hacia un escenario más cercano a producción.