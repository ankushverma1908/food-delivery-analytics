-- Advanced business questions for the synthetic food delivery dataset.
-- DuckDB. Register source files as food_delivery_orders, customers, restaurants.
-- This file intentionally uses window functions, CTEs, and cohort calculations.

-- 1. Monthly revenue with MoM growth
WITH monthly AS (
  SELECT DATE_TRUNC('month', order_date) AS month,
         SUM(net_amount) AS revenue
  FROM food_delivery_orders
  WHERE order_status = 'Delivered'
  GROUP BY 1
)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS previous_month_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
         / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_growth_pct
FROM monthly ORDER BY month;

-- 2. Cumulative revenue over time
WITH daily AS (
  SELECT CAST(order_date AS DATE) AS order_day, SUM(net_amount) AS daily_revenue
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY 1
)
SELECT order_day, daily_revenue,
       SUM(daily_revenue) OVER (ORDER BY order_day ROWS UNBOUNDED PRECEDING) AS cumulative_revenue
FROM daily ORDER BY order_day;

-- 3. Rank restaurants within each city
WITH performance AS (
  SELECT customer_city, restaurant_id, restaurant_name,
         SUM(net_amount) AS revenue
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY 1,2,3
)
SELECT *, DENSE_RANK() OVER (PARTITION BY customer_city ORDER BY revenue DESC) AS city_rank
FROM performance QUALIFY city_rank <= 5
ORDER BY customer_city, city_rank;

-- 4. Customer purchase frequency and revenue tiers
WITH customer_metrics AS (
  SELECT customer_id, COUNT(*) AS delivered_orders, SUM(net_amount) AS spend
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY customer_id
)
SELECT customer_id, delivered_orders, ROUND(spend, 2) AS spend,
       NTILE(5) OVER (ORDER BY spend) AS spend_quintile
FROM customer_metrics;

-- 5. Repeat customer rate by signup cohort
WITH first_order AS (
  SELECT customer_id, MIN(order_date) AS first_order_date
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY customer_id
),
orders_per_customer AS (
  SELECT customer_id, COUNT(*) AS delivered_orders
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY customer_id
)
SELECT STRFTIME(c.signup_date, '%Y-%m') AS signup_cohort,
       COUNT(*) AS customers,
       SUM(CASE WHEN f.customer_id IS NOT NULL THEN 1 ELSE 0 END) AS activated_customers,
       SUM(CASE WHEN o.delivered_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN o.delivered_orders > 1 THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0), 2) AS repeat_rate_pct
FROM customers c
LEFT JOIN first_order f USING (customer_id)
LEFT JOIN orders_per_customer o USING (customer_id)
GROUP BY 1 ORDER BY 1;

-- 6. City ranking by revenue contribution
WITH city_revenue AS (
  SELECT customer_city, SUM(net_amount) AS revenue
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY 1
)
SELECT customer_city, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct,
       RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM city_revenue ORDER BY revenue DESC;

-- 7. High-value customers with low recent activity (dataset-relative recency)
WITH customer_rfm AS (
  SELECT customer_id, MAX(order_date) AS last_order,
         COUNT(*) AS frequency, SUM(net_amount) AS monetary
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY customer_id
),
reference AS (SELECT MAX(order_date) + INTERVAL 1 DAY AS as_of_date FROM food_delivery_orders)
SELECT customer_id, frequency, ROUND(monetary,2) AS monetary,
       DATE_DIFF('day', last_order, as_of_date) AS recency_days
FROM customer_rfm CROSS JOIN reference
WHERE monetary >= (SELECT QUANTILE_CONT(monetary, 0.75) FROM customer_rfm)
  AND DATE_DIFF('day', last_order, as_of_date) >= 60
ORDER BY monetary DESC;

-- 8. Cancellation rate by hour
SELECT EXTRACT(HOUR FROM order_date) AS order_hour,
       COUNT(*) AS orders,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS cancellation_rate_pct
FROM food_delivery_orders GROUP BY 1 ORDER BY 1;

-- 9. Delivery time and rating bands
SELECT CASE WHEN delivery_time_mins < 25 THEN '<25 min'
            WHEN delivery_time_mins < 40 THEN '25-39 min'
            WHEN delivery_time_mins < 55 THEN '40-54 min'
            ELSE '55+ min' END AS time_band,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(customer_rating), 2) AS avg_rating
FROM food_delivery_orders WHERE order_status = 'Delivered'
GROUP BY 1 ORDER BY MIN(delivery_time_mins);

-- 10. Discount dependency: order mix by discount band
SELECT CASE WHEN discount = 0 THEN 'No discount'
            WHEN discount / NULLIF(order_value,0) <= 0.10 THEN '0-10%'
            WHEN discount / NULLIF(order_value,0) <= 0.15 THEN '10-15%'
            ELSE '15%+' END AS discount_band,
       COUNT(*) AS orders,
       ROUND(AVG(net_amount),2) AS avg_net_amount,
       ROUND(AVG(customer_rating),2) AS avg_rating
FROM food_delivery_orders WHERE order_status = 'Delivered'
GROUP BY 1 ORDER BY orders DESC;

-- 11. Restaurant revenue Pareto contribution
WITH ranked AS (
  SELECT restaurant_id, restaurant_name, SUM(net_amount) AS revenue
  FROM food_delivery_orders WHERE order_status = 'Delivered'
  GROUP BY 1,2
),
shares AS (
  SELECT *, revenue / SUM(revenue) OVER () AS revenue_share,
         SUM(revenue) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING)
           / SUM(revenue) OVER () AS cumulative_share
  FROM ranked
)
SELECT restaurant_id, restaurant_name, ROUND(revenue,2) AS revenue,
       ROUND(100*revenue_share,2) AS revenue_share_pct,
       ROUND(100*cumulative_share,2) AS cumulative_revenue_pct
FROM shares ORDER BY revenue DESC;

-- 12. Payment method performance
SELECT payment_mode, COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS delivery_success_pct
FROM food_delivery_orders GROUP BY 1 ORDER BY total_orders DESC;
