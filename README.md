# Food Delivery Intelligence & Business Analytics

An end-to-end portfolio project analysing a fictional multi-city food delivery platform using Python, SQL, and Power BI.

> **Data provenance:** The source dataset and all extension tables are synthetic and generated for portfolio practice. They are not actual Swiggy or Zomato data, customer records, menu prices, delivery-partner records, or marketing campaigns.

## Business questions

- How do order volume, delivered revenue, and average order value change over time?
- Which cities, cuisines, and restaurants contribute the most delivered revenue?
- What proportion of customers return to place another order?
- Which customer segments have high value or show signs of churn risk?
- How do preparation time, travel time, and delivery distance relate to delivery outcomes and ratings?
- Which menu categories and products contribute most to basket value?
- How are discount redemptions distributed across synthetic campaign types?

## Technology

Python (pandas, NumPy), SQL (DuckDB-compatible), Power BI (data model and DAX), Jupyter.

## Repository layout

```text
data/                 Original synthetic source CSVs and generators
data/extended/        Generated item, delivery, partner, and promotion tables
data/processed/       Power BI fact and dimension CSVs
data/analytics/       Reusable KPI, city, cuisine, restaurant, and RFM marts
notebooks/            Original exploratory analysis notebook
src/                  Reproducible Python pipelines
sql/                  Core and advanced business analysis queries
powerbi/              Model instructions and DAX measures
reports/              Data dictionary and generated quality report
docs/                 Architecture and metric definitions
tests/                Automated data integrity tests
```

## Quick start

Create and activate a virtual environment if desired, then run:

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/data_quality_report.py
python src/prepare_powerbi_data.py
python src/generate_extended_data.py
python src/build_analytics_marts.py
```

Generated tables are saved under `data/processed/`, `data/extended/`, and `data/analytics/`. Raw source CSVs are not overwritten.

## Power BI

1. Run the preparation and extension scripts above.
2. Import the CSV tables described in [powerbi/EXTENDED_MODEL.md](powerbi/EXTENDED_MODEL.md).
3. Create the documented one-to-many relationships and mark the calendar dimension as the Date table.
4. Add measures from [powerbi/DAX_Measures.dax](powerbi/DAX_Measures.dax) and [powerbi/Extended_DAX_Measures.dax](powerbi/Extended_DAX_Measures.dax).
5. Build five report pages: Executive Overview, Customer Analytics, Restaurant & Menu, Delivery Operations, and Campaign Analysis.

The repository includes the model plan and DAX definitions; the actual `.pbix` report must be created and saved in Power BI Desktop.

## SQL

Load the source and generated CSV files into DuckDB using the table names referenced in the SQL scripts. See:
- [Core business analysis](sql/business_analysis.sql)
- [Extended item, delivery, and promotion analysis](sql/extended_analysis.sql)
- [Advanced window-function and cohort questions](sql/advanced_business_questions.sql)

## Documentation

- [Upgrade guide](UPGRADE_GUIDE.md)
- [Project architecture and KPI definitions](docs/PROJECT_ARCHITECTURE.md)
- [Data dictionary](reports/DATA_DICTIONARY.md)
- [Extended Power BI model](powerbi/EXTENDED_MODEL.md)

## Important analytical limitations

- Item lines are simulated allocations that reconcile to the source order subtotal; they are not observed item-level transactions.
- Delivery distance, partner assignment, preparation/travel split, and partner ratings are simulated.
- Promotion labels are inferred from existing discount-rate bands and are not original coupon records.
- Use delivered orders for realized revenue. Keep cancelled and delayed outcomes distinct.
- Descriptive relationships (for example, delivery time and rating) must not be presented as causal proof.

## License

MIT. See [LICENSE](LICENSE).
