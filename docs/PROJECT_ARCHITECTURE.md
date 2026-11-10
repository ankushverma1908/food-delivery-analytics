# Project Architecture & Metric Definitions

## Business objective

Build a reproducible analytics workflow for a fictional multi-city food delivery platform. The goal is to understand demand, customer value, restaurant performance, delivery operations, and promotion usage, then translate findings into measurable business recommendations.

## Architecture

```text
Synthetic source CSVs
        |
        v
Python validation + preparation
        |
        +------> Data quality checks / automated tests
        |
        +------> Analytics marts (monthly, city, cuisine, restaurant, RFM)
        |
        +------> Power BI star-schema CSVs
        |
        +------> Extended synthetic facts (items, delivery, promotions)
                         |
                         v
                  SQL analysis layer
                         |
                         v
              Power BI semantic model
                         |
                         v
       Executive / Customer / Product / Operations / Campaign pages
```

## Metric definitions

| KPI | Definition |
|---|---|
| Total Orders | Distinct order IDs across all statuses |
| Delivered Orders | Distinct orders with status Delivered |
| Delivery Success Rate | Delivered Orders / Total Orders |
| Cancellation Rate | Cancelled Orders / Total Orders |
| Delay Rate | Delayed Orders / Total Orders |
| Delivered Revenue | Sum of net_amount for Delivered orders |
| Average Order Value | Delivered Revenue / Delivered Orders |
| Average Customer Rating | Average rating for Delivered orders |
| Average Delivery Time | Average delivery_time_mins for Delivered orders |
| Repeat Customer Rate | Customers with more than one delivered order / customers with at least one delivered order |
| Item Revenue | Sum of generated order-item line totals |
| Promotion Discount Investment | Sum of discount_amount in the promotion bridge |

## Analytical cautions

- This is synthetic portfolio data. Findings do not represent Swiggy, Zomato, or any real delivery company.
- Correlation between delivery time and rating is descriptive and does not establish causation.
- Delayed is a separate order status in the source data; do not silently count delayed orders as completed revenue.
- The extended item catalogue allocates each order's food subtotal across generated line items. Item prices are not real menu prices.
- Promotion names are synthetic labels mapped to discount bands, not observed coupon campaign IDs.
- Customer RFM uses the maximum delivered order date in the dataset as its reference date so that results are reproducible.
