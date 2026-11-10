-- Advanced analysis using the generated tables in data/extended/.
-- DuckDB examples. Register/import the CSVs as tables with the matching names.

-- 1. Item category revenue and units
SELECT m.item_category, SUM(i.quantity) AS units_sold,
       ROUND(SUM(i.line_total), 2) AS item_revenue
FROM FactOrderItems i
JOIN DimMenuItem m USING (menu_item_id)
GROUP BY 1 ORDER BY item_revenue DESC;

-- 2. Top menu items
SELECT item_name, SUM(quantity) AS units_sold,
       ROUND(SUM(line_total), 2) AS item_revenue
FROM FactOrderItems
GROUP BY 1 ORDER BY item_revenue DESC LIMIT 15;

-- 3. Average basket size by city (line count is equal to generated item count)
SELECT o.customer_city AS city, COUNT(DISTINCT o.order_id) AS orders,
       ROUND(AVG(x.item_lines), 2) AS avg_items_per_order
FROM food_delivery_orders o
JOIN (SELECT order_id, COUNT(*) AS item_lines FROM FactOrderItems GROUP BY order_id) x USING (order_id)
GROUP BY 1 ORDER BY avg_items_per_order DESC;

-- 4. Prep vs travel time by city
SELECT o.customer_city AS city,
       ROUND(AVG(d.prep_time_mins), 1) AS avg_prep_mins,
       ROUND(AVG(d.travel_time_mins), 1) AS avg_travel_mins,
       ROUND(AVG(d.distance_km), 2) AS avg_distance_km
FROM food_delivery_orders o
JOIN FactDelivery d USING (order_id)
WHERE d.delivery_outcome IN ('Delivered', 'Delayed')
GROUP BY 1 ORDER BY avg_travel_mins DESC;

-- 5. Delivery partner performance
SELECT p.delivery_partner_id, p.partner_city, p.partner_vehicle,
       p.partner_rating, COUNT(*) AS completed_or_delayed_orders,
       ROUND(AVG(d.travel_time_mins), 1) AS avg_travel_mins,
       ROUND(AVG(d.distance_km), 2) AS avg_distance_km
FROM FactDelivery d
JOIN DimDeliveryPartner p USING (delivery_partner_id)
WHERE d.delivery_outcome IN ('Delivered', 'Delayed')
GROUP BY 1,2,3,4
ORDER BY completed_or_delayed_orders DESC;

-- 6. Delayed order share by distance band
SELECT CASE WHEN distance_km < 3 THEN 'Under 3 km'
            WHEN distance_km < 7 THEN '3-7 km'
            WHEN distance_km < 11 THEN '7-11 km'
            ELSE '11+ km' END AS distance_band,
       COUNT(*) AS orders,
       ROUND(100.0 * SUM(CASE WHEN delivery_outcome = 'Delayed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS delayed_pct
FROM FactDelivery
WHERE delivery_outcome IN ('Delivered', 'Delayed')
GROUP BY 1 ORDER BY MIN(distance_km);

-- 7. Promotion redemptions and discount investment
SELECT p.coupon_code, p.campaign_name, COUNT(*) AS redemptions,
       ROUND(SUM(b.discount_amount), 2) AS discount_investment,
       ROUND(AVG(o.net_amount), 2) AS avg_order_net_amount
FROM BridgeOrderPromotion b
JOIN DimPromotion p USING (promotion_id)
JOIN food_delivery_orders o USING (order_id)
GROUP BY 1,2 ORDER BY redemptions DESC;

-- 8. Product category and cuisine cross-analysis
SELECT r.cuisine, m.item_category,
       SUM(i.quantity) AS units_sold,
       ROUND(SUM(i.line_total), 2) AS item_revenue
FROM FactOrderItems i
JOIN DimMenuItem m USING (menu_item_id)
JOIN food_delivery_orders o USING (order_id)
JOIN restaurants r USING (restaurant_id)
GROUP BY 1,2 ORDER BY item_revenue DESC;

-- 9. Reconcile item-level subtotal to order-level food value
SELECT COUNT(*) AS orders_with_value_mismatch
FROM (
  SELECT o.order_id, o.order_value, SUM(i.line_total) AS item_subtotal
  FROM food_delivery_orders o
  JOIN FactOrderItems i USING (order_id)
  GROUP BY 1,2
) x
WHERE ABS(x.order_value - x.item_subtotal) > 0.011;

-- 10. Partner ratings and delivery outcomes (descriptive, not causal)
SELECT p.partner_vehicle, d.delivery_outcome,
       COUNT(*) AS deliveries,
       ROUND(AVG(p.partner_rating), 2) AS avg_partner_rating,
       ROUND(AVG(d.travel_time_mins), 1) AS avg_travel_mins
FROM FactDelivery d
JOIN DimDeliveryPartner p USING (delivery_partner_id)
WHERE d.delivery_outcome IN ('Delivered', 'Delayed')
GROUP BY 1,2 ORDER BY 1,2;
