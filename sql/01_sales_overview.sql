
-- Overall sales performance
SELECT
    COUNT(*) AS total_orders,
    COUNT(total_sale) AS orders_with_recorded_sales,
    SUM(total_sale) AS total_revenue,
    ROUND(AVG(total_sale), 2) AS average_order_value
FROM sales;


-- Sales performance by year and month
SELECT
    year,
    month,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS monthly_revenue
FROM sales
GROUP BY year, month
ORDER BY year, month;


-- Sales performance by sales channel
SELECT
    sales_channel,
    COUNT(*) AS total_orders,
    SUM(total_sale) AS total_revenue
FROM sales
GROUP BY sales_channel
ORDER BY total_revenue DESC;


-- Check the date range of the dataset
SELECT
    MIN(sale_date) AS first_sale_date,
    MAX(sale_date) AS last_sale_date
FROM sales;


-- Check the completeness of sales values
SELECT
    COUNT(*) AS total_records,
    COUNT(units_sold) AS records_with_units,
    COUNT(unit_price) AS records_with_price,
    COUNT(total_sale) AS records_with_sales,
    COUNT(*) - COUNT(total_sale) AS missing_sales_values
FROM sales;
