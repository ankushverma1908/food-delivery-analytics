"""Build portfolio-ready analytical CSV marts from the synthetic source data.

Run from repository root:
    python src/build_analytics_marts.py

Outputs: data/analytics/ and reports/. Raw data is never modified.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "analytics"
REPORTS = ROOT / "reports"

def main():
    orders = pd.read_csv(DATA / "food_delivery_orders.csv", parse_dates=["order_date"])
    customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
    restaurants = pd.read_csv(DATA / "restaurants.csv")
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    orders["order_month"] = orders.order_date.dt.to_period("M").astype(str)
    orders["order_hour"] = orders.order_date.dt.hour
    orders["weekday"] = orders.order_date.dt.day_name()
    orders["is_weekend"] = orders.order_date.dt.dayofweek >= 5
    orders["discount_pct"] = np.where(orders.order_value.gt(0), orders.discount / orders.order_value, 0)

    delivered = orders.loc[orders.order_status.eq("Delivered")].copy()
    monthly = orders.groupby("order_month").agg(
        total_orders=("order_id", "nunique"),
        delivered_orders=("order_status", lambda s: s.eq("Delivered").sum()),
        cancelled_orders=("order_status", lambda s: s.eq("Cancelled").sum()),
        delayed_orders=("order_status", lambda s: s.eq("Delayed").sum()),
    ).reset_index()
    revenue = delivered.groupby("order_month").agg(
        delivered_revenue=("net_amount", "sum"),
        average_order_value=("net_amount", "mean"),
        average_rating=("customer_rating", "mean"),
    ).reset_index()
    monthly = monthly.merge(revenue, on="order_month", how="left")
    monthly["cancellation_rate"] = monthly.cancelled_orders / monthly.total_orders
    monthly["delay_rate"] = monthly.delayed_orders / monthly.total_orders
    monthly.to_csv(OUT / "monthly_kpis.csv", index=False)

    city = orders.groupby("customer_city").agg(
        total_orders=("order_id", "nunique"),
        delivered_orders=("order_status", lambda s: s.eq("Delivered").sum()),
        cancelled_orders=("order_status", lambda s: s.eq("Cancelled").sum()),
        delayed_orders=("order_status", lambda s: s.eq("Delayed").sum()),
    ).reset_index()
    city_rev = delivered.groupby("customer_city").agg(
        delivered_revenue=("net_amount", "sum"),
        avg_order_value=("net_amount", "mean"),
        avg_delivery_mins=("delivery_time_mins", "mean"),
        avg_rating=("customer_rating", "mean"),
    ).reset_index()
    city = city.merge(city_rev, on="customer_city", how="left")
    city["cancellation_rate"] = city.cancelled_orders / city.total_orders
    city["delay_rate"] = city.delayed_orders / city.total_orders
    city.to_csv(OUT / "city_performance.csv", index=False)

    cuisine = delivered.groupby("cuisine").agg(
        delivered_orders=("order_id", "nunique"),
        delivered_revenue=("net_amount", "sum"),
        avg_order_value=("net_amount", "mean"),
        avg_rating=("customer_rating", "mean"),
    ).reset_index().sort_values("delivered_revenue", ascending=False)
    cuisine.to_csv(OUT / "cuisine_performance.csv", index=False)

    restaurant = delivered.groupby(["restaurant_id", "restaurant_name", "customer_city", "cuisine"]).agg(
        delivered_orders=("order_id", "nunique"),
        delivered_revenue=("net_amount", "sum"),
        avg_order_value=("net_amount", "mean"),
        avg_delivery_mins=("delivery_time_mins", "mean"),
        avg_customer_rating=("customer_rating", "mean"),
    ).reset_index().sort_values("delivered_revenue", ascending=False)
    restaurant.to_csv(OUT / "restaurant_performance.csv", index=False)

    hourly = orders.groupby("order_hour").agg(
        total_orders=("order_id", "nunique"),
        delivered_orders=("order_status", lambda s: s.eq("Delivered").sum()),
    ).reset_index()
    hourly.to_csv(OUT / "hourly_demand.csv", index=False)

    # RFM uses delivered orders only. Recency reference is the maximum date in the
    # dataset, avoiding dependence on the computer's current date.
    reference_date = delivered.order_date.max().normalize() + pd.Timedelta(days=1)
    rfm = delivered.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("net_amount", "sum"),
    ).reset_index()
    rfm["recency_days"] = (reference_date - rfm.last_order_date.dt.normalize()).dt.days
    rfm["R_score"] = pd.qcut(rfm.recency_days.rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm.frequency.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm.monetary.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["rfm_score"] = rfm[["R_score", "F_score", "M_score"]].sum(axis=1)
    rfm["segment"] = np.select(
        [
            (rfm.R_score >= 4) & (rfm.F_score >= 4) & (rfm.M_score >= 4),
            (rfm.R_score >= 3) & (rfm.F_score >= 3),
            (rfm.R_score <= 2) & (rfm.F_score >= 3),
            (rfm.F_score <= 2),
        ],
        ["Champions", "Loyal Customers", "At Risk", "New / Low Frequency"],
        default="Potential Loyalists",
    )
    rfm.to_csv(OUT / "customer_rfm.csv", index=False)

    cohort = customers.copy()
    cohort["signup_month"] = cohort.signup_date.dt.to_period("M").astype(str)
    first_order = delivered.groupby("customer_id").order_date.min().rename("first_delivered_order").reset_index()
    cohort = cohort.merge(first_order, on="customer_id", how="left")
    cohort["first_order_month"] = cohort.first_delivered_order.dt.to_period("M").astype("string")
    cohort["activated"] = cohort.first_delivered_order.notna()
    cohort.to_csv(OUT / "customer_activation_cohort.csv", index=False)

    status = orders.groupby("order_status").agg(order_count=("order_id", "nunique")).reset_index()
    status["share"] = status.order_count / status.order_count.sum()
    status.to_csv(OUT / "order_status_mix.csv", index=False)

    print("Analytics marts generated:")
    for path in sorted(OUT.glob("*.csv")):
        print(f" - {path.relative_to(ROOT)} ({len(pd.read_csv(path)):,} rows)")
    print(f"RFM reference date: {reference_date.date()}")

if __name__ == "__main__":
    main()
