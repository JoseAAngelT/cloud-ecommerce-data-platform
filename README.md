Claro. Te dejo una versión completa para pegar en `README.md`, con tono técnico pero de nivel Jr, clara y sin exagerar el alcance.

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

* Clientes.
* Órdenes.
* Productos.
* Vendedores.
* Pagos.
* Reseñas.
* Entregas.
* Geolocalización.
* Traducción de categorías.

Los archivos originales se colocan en la carpeta:

```
data/landing/
```

Los datos no se incluyen en el repositorio para evitar subir archivos pesados o generados localmente.

---

## Objetivo técnico

Construir un flujo de datos que permita:

* Ingestar archivos CSV.
* Guardar datos crudos en capa Bronze.
* Limpiar y estandarizar datos en capa Silver.
* Crear tablas analíticas en capa Gold.
* Ejecutar validaciones de calidad.
* Generar un reporte de ejecución.
* Cargar las tablas Gold a PostgreSQL.
* Construir un dashboard en Power BI.

---

## Arquitectura del pipeline

El flujo principal del proyecto es:

```
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

---

## Capas de datos

### Bronze

La capa Bronze conserva una versión cercana a los datos originales.

En esta etapa se leen los archivos CSV desde `data/landing/` y se guardan en formato Parquet en `data/bronze/`.

También se agregan columnas técnicas de trazabilidad, como fecha de ingesta y archivo fuente.

### Silver

La capa Silver contiene datos limpios y estandarizados.

En esta etapa se realizan tareas como:

* Conversión de fechas.
* Conversión de columnas numéricas.
* Normalización de texto.
* Eliminación de duplicados.
* Estandarización de estados y categorías.
* Unión de productos con la traducción de categorías.

### Gold

La capa Gold contiene tablas listas para análisis.

Se construyeron dimensiones, hechos y tablas agregadas.

Dimensiones:

* `dim_customers`
* `dim_products`
* `dim_sellers`
* `dim_date`

Hechos:

* `fact_orders`
* `fact_order_items`
* `fact_payments`
* `fact_reviews`
* `fact_delivery`

Agregados de negocio:

* `agg_sales_by_month`
* `agg_sales_by_category`
* `agg_delivery_performance`
* `agg_seller_performance`
* `agg_customer_satisfaction`

---

## Calidad de datos

Después de generar la capa Gold se ejecutan validaciones de calidad.

Se implementaron dos tipos de validaciones:

### Validaciones propias en Python

Estas validaciones revisan:

* Existencia de tablas.
* Tablas no vacías.
* Columnas obligatorias.
* Nulos en campos críticos.
* Valores negativos en montos.
* Rangos válidos, como calificaciones entre 1 y 5.

### Validaciones con Great Expectations

También se incorporó Great Expectations para definir reglas más formales sobre las tablas analíticas.

Algunas validaciones aplicadas son:

* `order_id` no debe ser nulo.
* `payment_value` debe ser mayor o igual a 0.
* `review_score` debe estar entre 1 y 5.
* `order_status` debe pertenecer a valores esperados.
* Las tablas principales deben tener registros.

Los reportes de calidad se generan en:

```
outputs/quality/
```

---

## Reporte de ejecución

El pipeline genera un reporte general con el resumen de la ejecución.

El reporte incluye:

* Fecha de ejecución.
* Tablas procesadas por capa.
* Registros generados por tabla.
* Resultado de validaciones básicas.
* Resultado de validaciones con Great Expectations.
* Estado final del pipeline.

El archivo se genera en:

```
outputs/reports/execution_report.json
```

---

## Carga a PostgreSQL

Las tablas Gold se cargan a PostgreSQL en el esquema:

```
ecommerce_gold
```

Esta capa permite consultar los datos con SQL y conectar Power BI a una fuente estructurada.

Las credenciales se manejan con variables de entorno en un archivo `.env`, el cual no se sube al repositorio.

Ejemplo de configuración local:

```
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

```
docs/business_queries.sql
```

Algunos análisis incluidos son:

* Ventas mensuales.
* Top categorías por ventas.
* Top vendedores.
* Métodos de pago.
* Ventas por estado.
* Desempeño de entregas.
* Relación entre entrega tardía y calificación.
* Categorías con menor satisfacción.

También se documentaron los KPIs principales en:

```
docs/business_kpis.md
```

---

## Dashboard en Power BI

Se construyó un dashboard en Power BI conectado a PostgreSQL.

El archivo del dashboard se encuentra en:

```
dashboards/powerbi/ecommerce_dashboard.pbix
```

El dashboard incluye cuatro páginas:

### 1. Resumen Ejecutivo

Muestra los principales indicadores del negocio:

* Ventas totales.
* Órdenes totales.
* Ticket promedio.
* Calificación promedio.
* Tasa de entregas tardías.
* Ventas mensuales.
* Top categorías por ventas.

### 2. Análisis de ventas

Permite revisar el comportamiento comercial:

* Evolución mensual de ventas.
* Top categorías.
* Top vendedores.
* Valor pagado por método de pago.
* Detalle de vendedores.

### 3. Desempeño logístico

Permite analizar el comportamiento de entregas:

* Días promedio de entrega.
* Entregas totales.
* Entregas tardías.
* Tasa de entregas tardías.
* Entregas a tiempo vs tardías.
* Detalle mensual de entregas.

### 4. Satisfacción del cliente

Permite analizar la experiencia del cliente:

* Calificación promedio.
* Reseñas totales.
* Reseñas bajas.
* Reseñas altas.
* Calificación por mes.
* Categorías con menor satisfacción.
* Relación entre entrega tardía y calificación.

El diseño del dashboard está documentado en:

```
docs/dashboard_design.md
```

---

## Tecnologías utilizadas

* Python
* Pandas
* PyArrow
* Parquet
* PostgreSQL
* SQLAlchemy
* Great Expectations
* Power BI
* Ruff
* Git y GitHub

---

## Estructura del proyecto

```
cloud-ecommerce-data-platform/
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── landing/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── dashboards/
│   └── powerbi/
│
├── docs/
│   ├── business_kpis.md
│   ├── business_queries.sql
│   └── dashboard_design.md
│
├── outputs/
│   ├── quality/
│   └── reports/
│
├── src/
│   ├── ingest/
│   ├── load/
│   ├── quality/
│   ├── transform/
│   └── utils/
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Ejecución del proyecto

### 1. Crear entorno virtual

```
python -m venv .venv
```

### 2. Activar entorno virtual en Windows

```
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

### 4. Colocar archivos fuente

Colocar los CSV originales del dataset en:

```
data/landing/
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las credenciales de PostgreSQL.

Ejemplo:

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

### 6. Ejecutar pipeline

```
python main.py
```

---

## Flujo ejecutado por `main.py`

El archivo `main.py` ejecuta el pipeline en este orden:

1. Ingesta a Bronze.
2. Transformaciones Silver.
3. Construcción de Gold.
4. Validaciones básicas de calidad.
5. Validaciones con Great Expectations.
6. Generación de reporte de ejecución.
7. Carga de Gold a PostgreSQL.

---

## Convenciones de desarrollo

El proyecto utiliza Ruff para mantener un estilo de código consistente.

Comandos principales:

```
ruff check .
ruff check . --fix
ruff format .
```

---

## Estado actual

Versión local funcional.

Actualmente el proyecto permite ejecutar el pipeline completo, validar datos, cargar resultados a PostgreSQL y analizar la información en Power BI.

---

## Próximos pasos

Como mejora futura, se considera:

* Crear una versión de transformaciones con PySpark.
* Adaptar el almacenamiento a Azure Data Lake Storage Gen2.
* Orquestar el flujo con Azure Data Factory.
* Agregar infraestructura como código con Terraform.
* Incorporar Azure Key Vault para manejo de secretos.
* Preparar una versión cloud controlada del pipeline.

Estas mejoras no reemplazan la versión local, sino que buscan evolucionar el proyecto hacia un escenario más cercano a nube.
