
-- 1. Overall sales performance by state
SELECT
    state,
    COUNT(*) AS total_orders,
    SUM(units_sold) AS total_units_sold,
    SUM(total_sale) AS total_revenue,
    ROUND(AVG(total_sale), 2) AS average_order_value
FROM sales
GROUP BY state
ORDER BY total_revenue DESC;


-- 2. States ranked by number of orders
SELECT
    state,
    COUNT(*) AS total_orders
FROM sales
GROUP BY state
ORDER BY total_orders DESC;


-- 3. States ranked by units sold
SELECT
    state,
    SUM(units_sold) AS total_units_sold
FROM sales
GROUP BY state
ORDER BY total_units_sold DESC;


-- 4. Revenue contribution by state
SELECT
    state,
    SUM(total_sale) AS state_revenue,
    ROUND(
        SUM(total_sale) * 100.0 /
        NULLIF((SELECT SUM(total_sale) FROM sales), 0),
        2
    ) AS revenue_percentage
FROM sales
GROUP BY state
ORDER BY state_revenue DESC;


-- 5. Top-selling product in each state
SELECT
    state,
    product,
    SUM(units_sold) AS total_units_sold
FROM sales
GROUP BY state, product
ORDER BY state, total_units_sold DESC;
