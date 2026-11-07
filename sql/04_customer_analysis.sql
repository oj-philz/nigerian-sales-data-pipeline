
-- 1. Overall customer performance
SELECT
    customer_name,
    COUNT(*) AS total_orders,
    SUM(units_sold) AS total_units_purchased,
    SUM(total_sale) AS total_revenue,
    ROUND(AVG(total_sale), 2) AS average_order_value
FROM sales
GROUP BY customer_name
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by revenue
SELECT
    customer_name,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS total_revenue
FROM sales
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 10;


-- 3. Top 10 customers by number of orders
SELECT
    customer_name,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS total_revenue
FROM sales
GROUP BY customer_name
ORDER BY total_orders DESC
LIMIT 10;


-- 4. Customer purchasing activity by sales channel
SELECT
    customer_name,
    sales_channel,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS total_revenue
FROM sales
GROUP BY customer_name, sales_channel
ORDER BY customer_name, total_revenue DESC;


-- 5. Customer purchasing activity by state
SELECT
    customer_name,
    state,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS total_revenue
FROM sales
GROUP BY customer_name, state
ORDER BY customer_name, total_revenue DESC;


-- 6. Overall customer statistics
SELECT
    COUNT(DISTINCT customer_name) AS total_customers,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*)::NUMERIC / NULLIF(COUNT(DISTINCT customer_name), 0),
        2
    ) AS average_orders_per_customer,
    SUM(total_sale) AS total_revenue
FROM sales;
