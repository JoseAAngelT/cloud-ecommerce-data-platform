# Dashboard Design

## Objetivo

Construir un dashboard en Power BI para analizar ventas, desempeño logístico y satisfacción del cliente a partir de las tablas Gold cargadas en PostgreSQL.

El dashboard busca conectar la parte de ingeniería de datos con la parte analítica del proyecto, usando datos previamente procesados, validados y publicados en una base de datos de consumo.

## Fuente de datos

Las visualizaciones se conectan a PostgreSQL, usando la base de datos `ecommerce_dw` y el esquema:

`ecommerce_gold`

## Periodo analizado

El análisis principal considera el periodo de `2017-01` a `2018-08`.

Se eligió este rango porque el dataset contiene algunos meses parciales al inicio y al final, los cuales pueden generar caídas o picos que no representan necesariamente el comportamiento real del negocio.

## Páginas del dashboard

### 1. Resumen Ejecutivo

Muestra una vista general del negocio con los principales indicadores:

- Ventas totales.
- Órdenes totales.
- Ticket promedio.
- Calificación promedio.
- Tasa de entregas tardías.
- Ventas mensuales.
- Top categorías por ventas.

### 2. Análisis de ventas

Permite analizar el comportamiento comercial del negocio:

- Evolución mensual de ventas.
- Top categorías por ventas.
- Top vendedores por ventas.
- Ventas por método de pago.
- Detalle de principales vendedores.

### 3. Desempeño logístico

Permite revisar el comportamiento de las entregas:

- Días promedio de entrega.
- Entregas totales.
- Entregas tardías.
- Tasa de entregas tardías.
- Comparación entre entregas a tiempo y tardías.
- Detalle mensual de entregas.

### 4. Satisfacción del cliente

Permite analizar la experiencia del cliente a partir de las reseñas:

- Calificación promedio.
- Reseñas totales.
- Reseñas bajas.
- Reseñas altas.
- Evolución mensual de la calificación.
- Comparación entre reseñas bajas y altas.
- Categorías con menor satisfacción.
- Relación entre entrega tardía y calificación.

## Decisiones de modelado

Para el dashboard se priorizó el uso del modelo dimensional compuesto por tablas de hechos y dimensiones. Esto permite que los filtros de fecha funcionen de forma más consistente en las páginas del reporte.

Las tablas agregadas de Gold también se mantienen como salidas analíticas del pipeline, pero en el dashboard se utilizaron principalmente medidas DAX basadas en tablas `fact_` y `dim_`.

## Medidas principales

Algunas de las medidas DAX utilizadas son:

- Total Sales.
- Total Orders.
- Average Ticket.
- Average Delivery Days.
- Late Deliveries.
- Late Delivery Rate.
- Average Review Score.
- Total Reviews.
- Low Score Reviews.
- High Score Reviews.

## Uso esperado

El dashboard permite consultar información procesada desde la capa Gold para apoyar análisis de ventas, logística y satisfacción del cliente.

La intención no es construir un reporte empresarial definitivo, sino demostrar cómo un pipeline de ingeniería de datos puede entregar información lista para análisis y visualización.