
-- 1. Overall performance by product
SELECT
    product,
    COUNT(*) AS total_orders,
    SUM(units_sold) AS total_units_sold,
    SUM(total_sale) AS total_revenue,
    ROUND(AVG(total_sale), 2) AS average_order_value
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;


-- 2. Top-selling products by quantity
SELECT
    product,
    SUM(units_sold) AS total_units_sold
FROM sales
GROUP BY product
ORDER BY total_units_sold DESC
LIMIT 10;


-- 3. Products ranked by average selling price
SELECT
    product,
    ROUND(AVG(unit_price), 2) AS average_unit_price
FROM sales
GROUP BY product
ORDER BY average_unit_price DESC;


-- 4. Revenue contribution by product
SELECT
    product,
    SUM(total_sale) AS product_revenue,
    ROUND(
        SUM(total_sale) * 100.0 /
        NULLIF((SELECT SUM(total_sale) FROM sales), 0),
        2
    ) AS revenue_percentage
FROM sales
GROUP BY product
ORDER BY product_revenue DESC;


SELECT
    order_id,
    product,
    units_sold,
    unit_price,
    total_sale
FROM sales
WHERE units_sold <> TRUNC(units_sold)
ORDER BY product;


SELECT
    product,
    COUNT(*) AS fractional_records,
    SUM(units_sold) AS fractional_units_total
FROM sales
WHERE units_sold <> TRUNC(units_sold)
GROUP BY product;
