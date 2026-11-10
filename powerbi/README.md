# Power BI Report Build

1. Run `python src/prepare_powerbi_data.py`.
2. Import `data/processed/FactOrders.csv`, `DimCustomer.csv`, `DimRestaurant.csv`, and `DimDate.csv`.
3. Create 1-to-many relationships from each dimension to FactOrders using customer_id, restaurant_id, and DateKey.
4. Mark DimDate as the date table. Sort MonthName by MonthNo.
5. Add measures from DAX_Measures.dax and Extended_DAX_Measures.dax.
6. Import extended tables after running `python src/generate_extended_data.py`; relationship details are in EXTENDED_MODEL.md.

Suggested pages: Executive Overview, Customer Analytics, Restaurant & Menu, Delivery Operations, Campaign Analysis.

The actual PBIX file must be authored and saved in Power BI Desktop; DAX and model documentation are supplied here.
