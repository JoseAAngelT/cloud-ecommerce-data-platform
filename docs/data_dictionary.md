# Data Dictionary

## Descripción

Este documento describe las principales tablas generadas por el pipeline, con enfoque en la capa Gold.

La capa Gold contiene datos listos para análisis, consultas SQL y visualización en Power BI. Está compuesta por dimensiones, hechos y tablas agregadas.

---

## Capas del proyecto

### Bronze

Contiene una copia cercana a los archivos originales en formato Parquet.

### Silver

Contiene datos limpios y estandarizados.

### Gold

Contiene tablas analíticas listas para consumo.

---

# Gold Layer

## Dimensiones

---

## `dim_customers`

Contiene información de clientes.

| Columna                    | Descripción                             |
| -------------------------- | --------------------------------------- |
| `customer_id`              | Identificador del cliente en una orden. |
| `customer_unique_id`       | Identificador único del cliente.        |
| `customer_zip_code_prefix` | Prefijo de código postal del cliente.   |
| `customer_city`            | Ciudad del cliente.                     |
| `customer_state`           | Estado del cliente.                     |

Uso principal:

* Analizar ventas por ubicación del cliente.
* Relacionar órdenes con clientes.
* Crear visuales por estado o ciudad.

---

## `dim_products`

Contiene información de productos.

| Columna                         | Descripción                              |
| ------------------------------- | ---------------------------------------- |
| `product_id`                    | Identificador único del producto.        |
| `product_category_name`         | Categoría original del producto.         |
| `product_category_name_english` | Categoría traducida al inglés.           |
| `product_name_lenght`           | Longitud del nombre del producto.        |
| `product_description_lenght`    | Longitud de la descripción del producto. |
| `product_photos_qty`            | Número de fotos del producto.            |
| `product_weight_g`              | Peso del producto en gramos.             |
| `product_length_cm`             | Largo del producto en centímetros.       |
| `product_height_cm`             | Alto del producto en centímetros.        |
| `product_width_cm`              | Ancho del producto en centímetros.       |

Uso principal:

* Analizar ventas por categoría.
* Revisar categorías con mejor o peor desempeño.
* Relacionar productos vendidos con reseñas y órdenes.

---

## `dim_sellers`

Contiene información de vendedores.

| Columna                  | Descripción                            |
| ------------------------ | -------------------------------------- |
| `seller_id`              | Identificador único del vendedor.      |
| `seller_zip_code_prefix` | Prefijo de código postal del vendedor. |
| `seller_city`            | Ciudad del vendedor.                   |
| `seller_state`           | Estado del vendedor.                   |

Uso principal:

* Analizar ventas por vendedor.
* Revisar desempeño comercial por ciudad o estado.
* Identificar vendedores con mayor volumen de ventas.

---

## `dim_date`

Contiene información de fechas para análisis temporal.

| Columna      | Descripción                                   |
| ------------ | --------------------------------------------- |
| `date`       | Fecha calendario.                             |
| `date_id`    | Identificador de fecha en formato `YYYYMMDD`. |
| `year`       | Año.                                          |
| `month`      | Mes numérico.                                 |
| `day`        | Día del mes.                                  |
| `quarter`    | Trimestre.                                    |
| `year_month` | Año y mes en formato `YYYY-MM`.               |

Uso principal:

* Filtrar dashboards por mes.
* Analizar ventas, entregas y reseñas a lo largo del tiempo.
* Relacionar fechas con órdenes.

---

# Hechos

---

## `fact_orders`

Contiene información principal de órdenes.

| Columna                         | Descripción                                                      |
| ------------------------------- | ---------------------------------------------------------------- |
| `order_id`                      | Identificador único de la orden.                                 |
| `customer_id`                   | Identificador del cliente asociado a la orden.                   |
| `order_status`                  | Estado de la orden.                                              |
| `order_purchase_timestamp`      | Fecha y hora de compra.                                          |
| `order_approved_at`             | Fecha y hora de aprobación.                                      |
| `order_delivered_carrier_date`  | Fecha de entrega al transportista.                               |
| `order_delivered_customer_date` | Fecha de entrega al cliente.                                     |
| `order_estimated_delivery_date` | Fecha estimada de entrega.                                       |
| `purchase_date_id`              | Identificador de fecha de compra para relacionar con `dim_date`. |

Uso principal:

* Contar órdenes.
* Analizar estado de órdenes.
* Relacionar órdenes con clientes, fechas, pagos, entregas y reseñas.

---

## `fact_order_items`

Contiene los productos vendidos dentro de cada orden.

| Columna               | Descripción                                    |
| --------------------- | ---------------------------------------------- |
| `order_id`            | Identificador de la orden.                     |
| `order_item_id`       | Identificador del producto dentro de la orden. |
| `product_id`          | Identificador del producto vendido.            |
| `seller_id`           | Identificador del vendedor.                    |
| `shipping_limit_date` | Fecha límite de envío.                         |
| `price`               | Precio del producto.                           |
| `freight_value`       | Valor del flete.                               |
| `total_item_value`    | Suma de `price` y `freight_value`.             |

Uso principal:

* Calcular ventas totales.
* Analizar productos vendidos.
* Analizar vendedores.
* Calcular ticket promedio.

---

## `fact_payments`

Contiene información de pagos por orden.

| Columna                | Descripción                            |
| ---------------------- | -------------------------------------- |
| `order_id`             | Identificador de la orden.             |
| `payment_sequential`   | Secuencia del pago dentro de la orden. |
| `payment_type`         | Método de pago.                        |
| `payment_installments` | Número de pagos o cuotas.              |
| `payment_value`        | Valor pagado.                          |

Uso principal:

* Analizar métodos de pago.
* Calcular valor pagado por método.
* Revisar distribución de pagos.

---

## `fact_reviews`

Contiene información de reseñas de clientes.

| Columna                   | Descripción                           |
| ------------------------- | ------------------------------------- |
| `review_id`               | Identificador de la reseña.           |
| `order_id`                | Identificador de la orden reseñada.   |
| `review_score`            | Calificación otorgada por el cliente. |
| `review_creation_date`    | Fecha de creación de la reseña.       |
| `review_answer_timestamp` | Fecha de respuesta de la reseña.      |

Uso principal:

* Calcular calificación promedio.
* Analizar reseñas bajas y altas.
* Relacionar satisfacción con entregas y productos.

---

## `fact_delivery`

Contiene métricas relacionadas con entregas.

| Columna                         | Descripción                                    |
| ------------------------------- | ---------------------------------------------- |
| `order_id`                      | Identificador de la orden.                     |
| `order_purchase_timestamp`      | Fecha y hora de compra.                        |
| `order_delivered_customer_date` | Fecha de entrega al cliente.                   |
| `order_estimated_delivery_date` | Fecha estimada de entrega.                     |
| `delivery_days`                 | Días entre compra y entrega al cliente.        |
| `estimated_delivery_days`       | Días entre compra y fecha estimada de entrega. |
| `is_late_delivery`              | Indica si la entrega fue tardía.               |

Uso principal:

* Calcular tiempo promedio de entrega.
* Medir entregas tardías.
* Comparar entrega estimada contra entrega real.
* Analizar relación entre retrasos y calificación del cliente.

---

# Tablas agregadas

---

## `agg_sales_by_month`

Contiene ventas agregadas por mes.

| Columna         | Descripción                   |
| --------------- | ----------------------------- |
| `year_month`    | Año y mes de la venta.        |
| `total_orders`  | Total de órdenes del mes.     |
| `total_items`   | Total de artículos vendidos.  |
| `total_revenue` | Suma del precio de productos. |
| `total_freight` | Suma del valor de flete.      |
| `total_sales`   | Suma de ingresos y flete.     |

Uso principal:

* Analizar evolución mensual de ventas.
* Construir visuales de ventas por mes.
* Revisar crecimiento o caída de ingresos.

---

## `agg_sales_by_category`

Contiene ventas agregadas por categoría de producto.

| Columna                         | Descripción                                |
| ------------------------------- | ------------------------------------------ |
| `product_category_name_english` | Categoría del producto.                    |
| `total_orders`                  | Total de órdenes asociadas a la categoría. |
| `total_items`                   | Total de artículos vendidos.               |
| `total_revenue`                 | Suma del precio de productos.              |
| `total_freight`                 | Suma del valor de flete.                   |
| `total_sales`                   | Suma de ingresos y flete.                  |
| `avg_item_price`                | Precio promedio de los artículos.          |

Uso principal:

* Identificar categorías con mayores ventas.
* Comparar ingresos por tipo de producto.
* Apoyar visuales de ranking en Power BI.

---

## `agg_delivery_performance`

Contiene métricas logísticas agregadas por mes.

| Columna              | Descripción                     |
| -------------------- | ------------------------------- |
| `year_month`         | Año y mes de la orden.          |
| `total_orders`       | Total de órdenes.               |
| `delivered_orders`   | Total de órdenes entregadas.    |
| `avg_delivery_days`  | Promedio de días de entrega.    |
| `late_deliveries`    | Total de entregas tardías.      |
| `late_delivery_rate` | Proporción de entregas tardías. |

Uso principal:

* Analizar desempeño logístico mensual.
* Medir tasa de entregas tardías.
* Revisar evolución de tiempos de entrega.

---

## `agg_seller_performance`

Contiene métricas agregadas por vendedor.

| Columna          | Descripción                            |
| ---------------- | -------------------------------------- |
| `seller_id`      | Identificador del vendedor.            |
| `seller_city`    | Ciudad del vendedor.                   |
| `seller_state`   | Estado del vendedor.                   |
| `total_orders`   | Total de órdenes vendidas.             |
| `total_items`    | Total de artículos vendidos.           |
| `total_revenue`  | Suma del precio de productos vendidos. |
| `total_freight`  | Suma del valor de flete.               |
| `total_sales`    | Suma de ingresos y flete.              |
| `avg_item_price` | Precio promedio de artículos vendidos. |

Uso principal:

* Identificar vendedores con mayor venta.
* Revisar desempeño por vendedor.
* Crear rankings comerciales.

---

## `agg_customer_satisfaction`

Contiene métricas agregadas de satisfacción por mes.

| Columna              | Descripción                    |
| -------------------- | ------------------------------ |
| `year_month`         | Año y mes de la orden.         |
| `total_reviews`      | Total de reseñas.              |
| `avg_review_score`   | Calificación promedio.         |
| `low_score_reviews`  | Reseñas con calificación baja. |
| `high_score_reviews` | Reseñas con calificación alta. |
| `low_score_rate`     | Proporción de reseñas bajas.   |
| `high_score_rate`    | Proporción de reseñas altas.   |

Uso principal:

* Analizar satisfacción del cliente.
* Medir reseñas bajas y altas.
* Revisar evolución mensual de calificación.

---

# Métricas usadas en Power BI

Algunas medidas principales usadas en el dashboard son:

| Medida                  | Descripción                                         |
| ----------------------- | --------------------------------------------------- |
| `Total Sales`           | Ventas totales calculadas desde `fact_order_items`. |
| `Total Orders`          | Total de órdenes únicas.                            |
| `Average Ticket`        | Ventas totales divididas entre órdenes totales.     |
| `Payment Value`         | Valor total pagado.                                 |
| `Average Delivery Days` | Promedio de días de entrega.                        |
| `Late Deliveries`       | Total de entregas tardías.                          |
| `Late Delivery Rate`    | Proporción de entregas tardías.                     |
| `Average Review Score`  | Calificación promedio.                              |
| `Total Reviews`         | Total de reseñas.                                   |
| `Low Score Reviews`     | Reseñas con calificación menor o igual a 2.         |
| `High Score Reviews`    | Reseñas con calificación mayor o igual a 4.         |

---

# Notas

* Las tablas Gold se cargan a PostgreSQL en el esquema `ecommerce_gold`.
* El dashboard usa principalmente tablas `fact_` y `dim_` para mejorar el comportamiento de filtros.
* Las tablas agregadas se mantienen como salidas analíticas del pipeline.
* El periodo principal usado en el dashboard es de `2017-01` a `2018-08`, para evitar meses parciales del dataset.
