"""Generate richer synthetic tables for advanced food-delivery analytics.

Run from repository root:
    python src/generate_extended_data.py

Reads existing source CSVs and writes additional tables to data/extended/.
Original source files are never changed. All added records are synthetic.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "extended"
SEED = 20261110

MENU = [
    (1, "Chicken Biryani", "Biryani"), (2, "Veg Biryani", "Biryani"),
    (3, "Paneer Butter Masala", "North Indian"), (4, "Butter Naan", "North Indian"),
    (5, "Masala Dosa", "South Indian"), (6, "Idli Sambar", "South Indian"),
    (7, "Hakka Noodles", "Chinese"), (8, "Veg Manchurian", "Chinese"),
    (9, "Margherita Pizza", "Italian"), (10, "Farmhouse Pizza", "Italian"),
    (11, "Classic Burger", "Fast Food"), (12, "French Fries", "Fast Food"),
    (13, "Gulab Jamun", "Desserts"), (14, "Chocolate Brownie", "Desserts"),
    (15, "Grilled Sandwich", "Street Food"), (16, "Pav Bhaji", "Street Food"),
    (17, "Quinoa Bowl", "Healthy Food"), (18, "Grilled Salad", "Healthy Food"),
    (19, "Dal Makhani", "North Indian"), (20, "Chole Bhature", "North Indian"),
    (21, "Veg Fried Rice", "Chinese"), (22, "Chicken Momos", "Chinese"),
    (23, "Cold Coffee", "Beverages"), (24, "Fresh Lime Soda", "Beverages"),
    (25, "Tandoori Chicken", "North Indian"), (26, "Pasta Alfredo", "Italian"),
    (27, "Samosa", "Street Food"), (28, "Rasgulla", "Desserts"),
    (29, "Rava Dosa", "South Indian"), (30, "Fruit Bowl", "Healthy Food"),
]

def main():
    rng = np.random.default_rng(SEED)
    orders = pd.read_csv(DATA / "food_delivery_orders.csv", parse_dates=["order_date"])
    restaurants = pd.read_csv(DATA / "restaurants.csv")

    OUT.mkdir(parents=True, exist_ok=True)

    # Menu catalogue is a synthetic catalogue, not a real restaurant menu.
    menu = pd.DataFrame(MENU, columns=["menu_item_id", "item_name", "item_category"])
    menu.to_csv(OUT / "DimMenuItem.csv", index=False)

    # Build line items whose count and total value reconcile exactly to source orders.
    menu_by_category = {
        category: group.menu_item_id.to_numpy()
        for category, group in menu.groupby("item_category")
    }
    menu_lookup = menu.set_index("menu_item_id")["item_name"].to_dict()
    item_rows = []
    for row in orders.itertuples(index=False):
        category = row.cuisine if row.cuisine in menu_by_category else "Street Food"
        choices = menu_by_category[category]
        count = max(1, int(row.items_count))
        ids = rng.choice(choices, size=count, replace=True)
        # Allocate the source order_value across line items; the final line absorbs rounding.
        weights = rng.uniform(0.6, 1.4, size=count)
        raw = float(row.order_value) * weights / weights.sum()
        amounts = np.round(raw, 2)
        amounts[-1] = round(float(row.order_value) - float(amounts[:-1].sum()), 2)
        for sequence, (menu_id, amount) in enumerate(zip(ids, amounts), start=1):
            item_rows.append({
                "order_id": int(row.order_id),
                "line_number": sequence,
                "menu_item_id": int(menu_id),
                "item_name": menu_lookup[int(menu_id)],
                "quantity": 1,
                "unit_price": round(float(amount), 2),
                "line_total": round(float(amount), 2),
            })
    order_items = pd.DataFrame(item_rows)
    order_items.to_csv(OUT / "FactOrderItems.csv", index=False)

    # Synthetic delivery-partner dimension.
    partner_count = 350
    cities = sorted(orders.customer_city.dropna().unique())
    partners = pd.DataFrame({
        "delivery_partner_id": np.arange(1, partner_count + 1),
        "partner_city": rng.choice(cities, partner_count),
        "partner_experience_months": rng.integers(1, 61, partner_count),
        "partner_vehicle": rng.choice(["Bike", "Scooter", "Bicycle"], partner_count, p=[0.48, 0.47, 0.05]),
        "partner_rating": np.round(np.clip(rng.normal(4.35, 0.35, partner_count), 3.0, 5.0), 2),
    })
    partners.to_csv(OUT / "DimDeliveryPartner.csv", index=False)

    # One operational record per order. Completed/delayed orders get a partner and
    # timestamps that reconcile to the existing delivery_time_mins value.
    partner_ids = partners.delivery_partner_id.to_numpy()
    delivery_rows = []
    for row in orders.itertuples(index=False):
        status = str(row.order_status)
        if status == "Cancelled":
            cancel_min = int(rng.integers(2, 16))
            delivery_rows.append({
                "order_id": int(row.order_id), "delivery_partner_id": pd.NA,
                "distance_km": round(float(rng.uniform(1, 12)), 2),
                "prep_time_mins": pd.NA, "travel_time_mins": pd.NA,
                "assigned_at": pd.NaT, "picked_up_at": pd.NaT,
                "completed_at": pd.NaT,
                "cancelled_at": row.order_date + pd.Timedelta(minutes=cancel_min),
                "delivery_outcome": "Cancelled",
            })
        else:
            total = max(2, int(row.delivery_time_mins))
            prep = int(rng.integers(8, max(9, min(31, total))))
            prep = min(prep, total - 1)
            travel = total - prep
            assigned = row.order_date + pd.Timedelta(minutes=2)
            pickup = assigned + pd.Timedelta(minutes=prep)
            completed = row.order_date + pd.Timedelta(minutes=total)
            delivery_rows.append({
                "order_id": int(row.order_id),
                "delivery_partner_id": int(rng.choice(partner_ids)),
                "distance_km": round(float(rng.uniform(0.8, 14)), 2),
                "prep_time_mins": prep, "travel_time_mins": travel,
                "assigned_at": assigned, "picked_up_at": pickup,
                "completed_at": completed, "cancelled_at": pd.NaT,
                "delivery_outcome": status,
            })
    delivery = pd.DataFrame(delivery_rows)
    delivery.to_csv(OUT / "FactDelivery.csv", index=False)

    # Promotion dimension and order-to-promotion bridge, based on the existing
    # discount amount. This adds campaign labels without changing source discounts.
    promotions = pd.DataFrame([
        (1, "WELCOME10", "New Customer", "Acquisition", 0.10),
        (2, "WEEKEND15", "Weekend Offer", "Engagement", 0.15),
        (3, "SAVE20", "Seasonal Savings", "Retention", 0.20),
    ], columns=["promotion_id", "coupon_code", "campaign_name", "campaign_type", "discount_rate"])
    promotions.to_csv(OUT / "DimPromotion.csv", index=False)

    promo_rows = []
    for row in orders.itertuples(index=False):
        if float(row.discount) <= 0 or float(row.order_value) <= 0:
            continue
        rate = float(row.discount) / float(row.order_value)
        promo_id = min([(1, 0.10), (2, 0.15), (3, 0.20)], key=lambda x: abs(x[1] - rate))[0]
        promo_rows.append({
            "order_id": int(row.order_id),
            "promotion_id": promo_id,
            "discount_amount": round(float(row.discount), 2),
        })
    bridge = pd.DataFrame(promo_rows)
    bridge.to_csv(OUT / "BridgeOrderPromotion.csv", index=False)

    # Reconciliation summary for quick validation.
    item_check = order_items.groupby("order_id").agg(
        generated_lines=("line_number", "count"),
        generated_item_value=("line_total", "sum")
    )
    check = orders.set_index("order_id")[["items_count", "order_value"]].join(item_check)
    count_mismatches = int((check.items_count != check.generated_lines).sum())
    value_mismatches = int(((check.order_value - check.generated_item_value).abs() > 0.011).sum())
    print(f"Created {len(order_items):,} item lines for {len(orders):,} orders")
    print(f"Created {len(partners):,} delivery partners and {len(delivery):,} delivery records")
    print(f"Created {len(promotions):,} promotions and {len(bridge):,} promotion redemptions")
    print(f"Item count mismatches: {count_mismatches}; item value mismatches: {value_mismatches}")
    if count_mismatches or value_mismatches:
        raise ValueError("Order-item reconciliation failed; inspect generated tables.")
    print(f"Extended data saved under: {OUT}")

if __name__ == "__main__":
    main()
