# Data Dictionary

All records are synthetic.

## food_delivery_orders.csv
- order_id: unique order key
- customer_id: customer foreign key
- customer_city: customer city
- restaurant_id / restaurant_name: restaurant key and label
- cuisine: cuisine category
- order_date: order timestamp
- items_count: number of generated items in basket
- order_value: food subtotal before fees and discounts
- delivery_fee: delivery fee
- discount: discount amount
- net_amount: order_value + delivery_fee - discount
- payment_mode: payment method
- delivery_time_mins: simulated total delivery duration
- order_status: Delivered, Cancelled, or Delayed
- customer_rating: 1–5 rating, missing for non-delivered orders

## customers.csv
customer_id, city, signup_date.

## restaurants.csv
restaurant_id, restaurant_name, city, cuisine, avg_rating.

Generated item prices, delivery partner attributes, distance, and promotion labels are synthetic extensions. See UPGRADE_GUIDE.md for assumptions and limitations.
