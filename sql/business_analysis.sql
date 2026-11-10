-- Core business analysis questions. Load source CSV as food_delivery_orders.
SELECT order_status, COUNT(*) AS orders FROM food_delivery_orders GROUP BY 1 ORDER BY 2 DESC;
SELECT DATE_TRUNC('month',order_date) AS month, COUNT(*) AS orders,
       SUM(CASE WHEN order_status='Delivered' THEN net_amount ELSE 0 END) AS delivered_revenue
FROM food_delivery_orders GROUP BY 1 ORDER BY 1;
SELECT customer_city, COUNT(*) AS orders,
       SUM(CASE WHEN order_status='Delivered' THEN net_amount ELSE 0 END) AS delivered_revenue
FROM food_delivery_orders GROUP BY 1 ORDER BY 3 DESC;
SELECT cuisine, COUNT(*) AS orders,
       SUM(CASE WHEN order_status='Delivered' THEN net_amount ELSE 0 END) AS delivered_revenue,
       AVG(CASE WHEN order_status='Delivered' THEN customer_rating END) AS avg_rating
FROM food_delivery_orders GROUP BY 1 ORDER BY 3 DESC;
SELECT payment_mode, COUNT(*) AS orders FROM food_delivery_orders GROUP BY 1 ORDER BY 2 DESC;
SELECT EXTRACT(HOUR FROM order_date) AS order_hour, COUNT(*) AS orders
FROM food_delivery_orders GROUP BY 1 ORDER BY 1;
SELECT customer_id, COUNT(*) AS delivered_orders, SUM(net_amount) AS delivered_spend
FROM food_delivery_orders WHERE order_status='Delivered'
GROUP BY 1 ORDER BY 3 DESC LIMIT 20;
SELECT restaurant_id, restaurant_name, SUM(net_amount) AS delivered_revenue
FROM food_delivery_orders WHERE order_status='Delivered'
GROUP BY 1,2 ORDER BY 3 DESC LIMIT 10;
SELECT order_status, AVG(delivery_time_mins) AS avg_delivery_minutes
FROM food_delivery_orders GROUP BY 1;
SELECT CASE WHEN discount=0 THEN 'No discount' ELSE 'Discounted' END AS discount_group,
       COUNT(*) AS orders, AVG(net_amount) AS avg_net_amount
FROM food_delivery_orders WHERE order_status='Delivered' GROUP BY 1;
