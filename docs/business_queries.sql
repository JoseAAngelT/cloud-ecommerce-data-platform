-- ============================================================
-- Business Queries - Cloud E-Commerce Data Platform
-- ============================================================

-- 1. Ventas mensuales
SELECT
    year_month,
    total_orders,
    total_items,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_freight::numeric, 2) AS total_freight,
    ROUND(total_sales::numeric, 2) AS total_sales
FROM ecommerce_gold.agg_sales_by_month
ORDER BY year_month;


-- 2. Top 10 categorías con mayores ventas
SELECT
    product_category_name_english,
    total_orders,
    total_items,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_sales::numeric, 2) AS total_sales,
    ROUND(avg_item_price::numeric, 2) AS avg_item_price
FROM ecommerce_gold.agg_sales_by_category
ORDER BY total_sales DESC
LIMIT 10;


-- 3. Desempeño de entregas por mes
SELECT
    year_month,
    total_orders,
    delivered_orders,
    ROUND(avg_delivery_days::numeric, 2) AS avg_delivery_days,
    late_deliveries,
    ROUND((late_delivery_rate * 100)::numeric, 2) AS late_delivery_rate_pct
FROM ecommerce_gold.agg_delivery_performance
ORDER BY year_month;


-- 4. Top 10 vendedores por ventas
SELECT
    seller_id,
    seller_city,
    seller_state,
    total_orders,
    total_items,
    ROUND(total_revenue::numeric, 2) AS total_revenue,
    ROUND(total_sales::numeric, 2) AS total_sales,
    ROUND(avg_item_price::numeric, 2) AS avg_item_price
FROM ecommerce_gold.agg_seller_performance
ORDER BY total_sales DESC
LIMIT 10;


-- 5. Satisfacción del cliente por mes
SELECT
    year_month,
    total_reviews,
    ROUND(avg_review_score::numeric, 2) AS avg_review_score,
    low_score_reviews,
    high_score_reviews,
    ROUND((low_score_rate * 100)::numeric, 2) AS low_score_rate_pct,
    ROUND((high_score_rate * 100)::numeric, 2) AS high_score_rate_pct
FROM ecommerce_gold.agg_customer_satisfaction
ORDER BY year_month;


-- 6. Métodos de pago más utilizados
SELECT
    payment_type,
    COUNT(*) AS total_payments,
    ROUND(SUM(payment_value)::numeric, 2) AS total_payment_value,
    ROUND(AVG(payment_value)::numeric, 2) AS avg_payment_value
FROM ecommerce_gold.fact_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- 7. Órdenes por estado
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM ecommerce_gold.fact_orders o
INNER JOIN ecommerce_gold.dim_customers c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_orders DESC;


-- 8. Ventas por estado del cliente
SELECT
    c.customer_state,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(SUM(oi.total_item_value)::numeric, 2) AS total_sales
FROM ecommerce_gold.fact_order_items oi
INNER JOIN ecommerce_gold.fact_orders o
    ON oi.order_id = o.order_id
INNER JOIN ecommerce_gold.dim_customers c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_sales DESC;


-- 9. Relación entre entrega tardía y calificación
SELECT
    d.is_late_delivery,
    COUNT(DISTINCT d.order_id) AS total_orders,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_score
FROM ecommerce_gold.fact_delivery d
INNER JOIN ecommerce_gold.fact_reviews r
    ON d.order_id = r.order_id
WHERE d.is_late_delivery IS NOT NULL
GROUP BY d.is_late_delivery
ORDER BY d.is_late_delivery;


-- 10. Categorías con menor calificación promedio
SELECT
    p.product_category_name_english,
    COUNT(DISTINCT r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_score
FROM ecommerce_gold.fact_reviews r
INNER JOIN ecommerce_gold.fact_order_items oi
    ON r.order_id = oi.order_id
INNER JOIN ecommerce_gold.dim_products p
    ON oi.product_id = p.product_id
WHERE p.product_category_name_english IS NOT NULL
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT r.review_id) >= 50
ORDER BY avg_review_score ASC
LIMIT 10;