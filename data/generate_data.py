"""
Generates a synthetic Swiggy/Zomato-style food delivery dataset.
Run: python generate_data.py
Produces: food_delivery_orders.csv in the same folder.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N_ORDERS = 15000
N_CUSTOMERS = 2500
N_RESTAURANTS = 180

cities = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata"]
cuisines = ["North Indian", "South Indian", "Chinese", "Italian", "Fast Food",
            "Desserts", "Biryani", "Continental", "Street Food", "Healthy Food"]
payment_modes = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Wallet"]
order_status = ["Delivered", "Delivered", "Delivered", "Delivered", "Cancelled", "Delayed"]

# Restaurants
restaurants = pd.DataFrame({
    "restaurant_id": range(1, N_RESTAURANTS + 1),
    "restaurant_name": [f"Restaurant_{i}" for i in range(1, N_RESTAURANTS + 1)],
    "city": np.random.choice(cities, N_RESTAURANTS),
    "cuisine": np.random.choice(cuisines, N_RESTAURANTS),
    "avg_rating": np.round(np.random.uniform(3.0, 4.9, N_RESTAURANTS), 1),
})

# Customers
customers = pd.DataFrame({
    "customer_id": range(1, N_CUSTOMERS + 1),
    "city": np.random.choice(cities, N_CUSTOMERS),
    "signup_date": [
        (datetime(2024, 1, 1) + timedelta(days=int(d)))
        for d in np.random.uniform(0, 545, N_CUSTOMERS)
    ],
})

start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 7, 1)
date_range_days = (end_date - start_date).days

rows = []
for order_id in range(1, N_ORDERS + 1):
    cust = customers.sample(1).iloc[0]
    rest = restaurants[restaurants.city == cust.city].sample(1).iloc[0] \
        if not restaurants[restaurants.city == cust.city].empty else restaurants.sample(1).iloc[0]

    order_date = start_date + timedelta(
        days=random.randint(0, date_range_days),
        hours=random.randint(7, 23),
        minutes=random.randint(0, 59)
    )
    items_count = np.random.poisson(2) + 1
    base_price = np.random.uniform(80, 150)
    order_value = round(base_price * items_count * np.random.uniform(0.9, 1.3), 2)
    delivery_fee = round(np.random.uniform(15, 60), 2)
    discount = round(order_value * np.random.choice([0, 0, 0.1, 0.15, 0.2]), 2)
    status = random.choice(order_status)
    delivery_time_mins = int(np.random.normal(35, 10)) if status != "Delayed" else int(np.random.normal(60, 12))
    delivery_time_mins = max(10, delivery_time_mins)

    rows.append({
        "order_id": order_id,
        "customer_id": cust.customer_id,
        "customer_city": cust.city,
        "restaurant_id": rest.restaurant_id,
        "restaurant_name": rest.restaurant_name,
        "cuisine": rest.cuisine,
        "order_date": order_date,
        "items_count": items_count,
        "order_value": order_value,
        "delivery_fee": delivery_fee,
        "discount": discount,
        "net_amount": round(order_value + delivery_fee - discount, 2),
        "payment_mode": random.choice(payment_modes),
        "delivery_time_mins": delivery_time_mins,
        "order_status": status,
        "customer_rating": np.random.choice([1,2,3,4,5], p=[0.03,0.05,0.12,0.35,0.45])
                            if status == "Delivered" else np.nan,
    })

orders = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)

orders.to_csv("food_delivery_orders.csv", index=False)
restaurants.to_csv("restaurants.csv", index=False)
customers.to_csv("customers.csv", index=False)

print(f"Generated {len(orders)} orders, {len(restaurants)} restaurants, {len(customers)} customers.")
