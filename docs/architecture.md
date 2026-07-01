# Architecture

## Descripción general

Este proyecto sigue una arquitectura de datos por capas, basada en el modelo Bronze, Silver y Gold.

La solución procesa archivos CSV de e-commerce, los transforma en tablas limpias y finalmente genera salidas analíticas que pueden consultarse desde PostgreSQL y Power BI.

La primera versión está desarrollada de forma local, pero la estructura del proyecto está pensada para poder evolucionar hacia una arquitectura en nube.

---

## Flujo general

El flujo principal del pipeline es:

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

---

## Landing

La carpeta `data/landing/` representa la zona donde llegan los archivos fuente.

En esta etapa los archivos se conservan en formato CSV, tal como fueron descargados del dataset original.

Esta carpeta funciona como punto de entrada del pipeline.

---

## Bronze

La capa Bronze guarda una copia cercana al dato original.

En esta etapa se leen los archivos CSV desde `data/landing/` y se convierten a formato Parquet en `data/bronze/`.

No se aplican reglas de negocio ni transformaciones analíticas. Solo se agregan columnas técnicas para trazabilidad:

* Fecha de ingesta.
* Nombre del archivo fuente.

El objetivo de Bronze es mantener una versión cruda del dato para poder reprocesar información si fuera necesario.

---

## Silver

La capa Silver contiene datos limpios y estandarizados.

En esta etapa se aplican transformaciones como:

* Conversión de fechas.
* Conversión de columnas numéricas.
* Normalización de textos.
* Estandarización de estados.
* Eliminación de duplicados.
* Unión de productos con la tabla de traducción de categorías.

El objetivo de Silver es dejar los datos consistentes y preparados para modelado analítico.

---

## Gold

La capa Gold contiene las tablas listas para análisis.

En esta etapa se construyen dimensiones, hechos y tablas agregadas.

### Dimensiones

* `dim_customers`
* `dim_products`
* `dim_sellers`
* `dim_date`

### Hechos

* `fact_orders`
* `fact_order_items`
* `fact_payments`
* `fact_reviews`
* `fact_delivery`

### Agregados

* `agg_sales_by_month`
* `agg_sales_by_category`
* `agg_delivery_performance`
* `agg_seller_performance`
* `agg_customer_satisfaction`

Las tablas Gold se usan como base para consultas SQL, validaciones finales y visualización en Power BI.

---

## Modelo analítico

El modelo analítico se apoya principalmente en tablas de hechos y dimensiones.

Relaciones principales:

```text
dim_customers → fact_orders
dim_date → fact_orders
fact_orders → fact_order_items
fact_orders → fact_payments
fact_orders → fact_reviews
fact_orders → fact_delivery
dim_products → fact_order_items
dim_sellers → fact_order_items
```

Las tablas agregadas también se generan en Gold, pero en Power BI se prioriza el uso de tablas `fact_` y `dim_` para tener filtros más consistentes.

---

## Calidad de datos

Después de construir Gold, el pipeline ejecuta validaciones de calidad.

Se usan dos enfoques:

### Validaciones propias en Python

Estas validaciones revisan:

* Que las tablas existan.
* Que no estén vacías.
* Que tengan columnas obligatorias.
* Que no existan nulos en campos críticos.
* Que los montos no sean negativos.
* Que las calificaciones estén en un rango válido.

### Validaciones con Great Expectations

Great Expectations se utiliza para definir reglas más formales sobre tablas Gold.

Algunas reglas aplicadas son:

* `order_id` no debe ser nulo.
* `payment_value` debe ser mayor o igual a 0.
* `review_score` debe estar entre 1 y 5.
* `order_status` debe pertenecer a valores esperados.

Los resultados se guardan en:

```text
outputs/quality/
```

---

## Reporte de ejecución

El pipeline genera un reporte general de ejecución en formato JSON.

Este reporte incluye:

* Fecha de ejecución.
* Tablas procesadas por capa.
* Número de registros por tabla.
* Resultado de validaciones básicas.
* Resultado de validaciones con Great Expectations.
* Estado final del pipeline.

Ubicación:

```text
outputs/reports/execution_report.json
```

---

## Capa de consumo

Las tablas Gold se cargan a PostgreSQL en el esquema:

```text
ecommerce_gold
```

PostgreSQL funciona como capa de consumo para:

* Consultas SQL.
* Validación de resultados.
* Conexión con Power BI.

El dashboard de Power BI se conecta a PostgreSQL y utiliza principalmente el modelo dimensional para análisis de ventas, logística y satisfacción.

---

## Seguridad y configuración

Las credenciales de PostgreSQL no se escriben directamente en el código.

Se manejan mediante variables de entorno en un archivo `.env`, el cual no se sube al repositorio.

Ejemplo:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

Esta decisión evita exponer contraseñas y permite cambiar la configuración sin modificar el código fuente.

---

## Decisiones técnicas

### Uso de Parquet

Se utiliza Parquet en las capas Bronze, Silver y Gold porque conserva mejor los tipos de datos y es más eficiente que CSV para lectura y escritura.

### Separación por capas

La separación Bronze, Silver y Gold permite mantener ordenado el flujo de datos:

* Bronze conserva el dato original.
* Silver limpia y estandariza.
* Gold prepara información para análisis.

### Uso de PostgreSQL

PostgreSQL se usa como base de consumo analítico local. Esto permite consultar las tablas Gold con SQL y conectar Power BI a una fuente estructurada.

### Uso de Power BI

Power BI se usa para construir un dashboard con indicadores de ventas, desempeño logístico y satisfacción del cliente.

### Uso de Great Expectations

Great Expectations se incorpora para mejorar la capa de calidad de datos y definir validaciones más formales.

---

## Estado actual

La arquitectura actual está implementada de forma local.

El pipeline permite:

* Procesar datos desde archivos CSV.
* Generar capas Bronze, Silver y Gold.
* Ejecutar validaciones de calidad.
* Crear reportes de ejecución.
* Cargar resultados a PostgreSQL.
* Analizar información en Power BI.

---

## Evolución futura

Como mejora futura, esta arquitectura puede evolucionar hacia nube usando servicios como:

* Azure Data Lake Storage Gen2.
* Azure Data Factory.
* Azure Databricks o PySpark.
* Azure SQL Database.
* Azure Key Vault.
* Terraform.

La versión local permite validar primero la lógica del pipeline antes de implementar servicios cloud.
