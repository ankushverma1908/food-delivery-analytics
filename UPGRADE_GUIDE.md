# Food Delivery Analytics — Extended Portfolio Upgrade

This upgrade is being developed on the `upgrade/food-delivery-powerbi` branch. The original `main` branch and its source files remain unchanged.

## What is new

The existing project starts with synthetic order, customer, and restaurant data. The extension adds a reproducible data generator for:

- **Menu catalogue and order lines:** item-level mix, quantity, basket composition, and product/category revenue.
- **Delivery partner dimension and delivery fact:** simulated partner assignments, distance, preparation time, travel time, and delivery outcome.
- **Promotion dimension and redemption bridge:** synthetic campaign labels and order-level discount allocations.

The generated tables are written to `data/extended/`. They are not actual Swiggy/Zomato records or actual partner/campaign data.

## Run locally

From the repository root:

```bash
pip install -r requirements.txt
python src/generate_extended_data.py
```

The generator reads the existing files under `data/` and writes only to `data/extended/`. It does not modify the raw CSVs or the original notebook.

## What can now be analysed

1. Product and cuisine mix, item-level revenue, and top-selling menu items.
2. Average basket size and order composition by city.
3. Preparation time versus travel time, delivery distance, and delayed-order share.
4. Delivery-partner workload and simulated partner ratings.
5. Coupon redemptions, discount investment, and promotional order value.

## Power BI

See [powerbi/EXTENDED_MODEL.md](powerbi/EXTENDED_MODEL.md) for import instructions, relationships, and dashboard ideas. Additional measures are in [powerbi/Extended_DAX_Measures.dax](powerbi/Extended_DAX_Measures.dax).

## SQL

See [sql/extended_analysis.sql](sql/extended_analysis.sql) for advanced queries. Register the CSVs as tables using the filenames (without `.csv`) before running the queries in DuckDB.

## Data integrity and limitations

- Item lines are allocated to each source order and reconciled to the original `order_value`; individual item prices are simulated allocations, not observed menu prices.
- The number of generated item lines matches the source `items_count` for each order.
- Delivery times are split into simulated preparation and travel components. Cancelled orders have no assigned partner.
- Promotion labels are inferred from discount-rate bands; they are not original coupon redemptions.
- These tables are suitable for portfolio demonstrations and analytical practice. Do not describe their patterns as real company performance or causal findings.
