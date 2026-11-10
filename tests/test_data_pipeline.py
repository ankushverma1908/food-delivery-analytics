"""Basic integrity tests for the synthetic food-delivery source data.

Run from repository root: python -m unittest discover -s tests -v
"""
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

class FoodDeliveryDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders = pd.read_csv(DATA / "food_delivery_orders.csv")
        cls.customers = pd.read_csv(DATA / "customers.csv")
        cls.restaurants = pd.read_csv(DATA / "restaurants.csv")

    def test_order_ids_unique(self):
        self.assertTrue(self.orders.order_id.is_unique)

    def test_customer_ids_unique(self):
        self.assertTrue(self.customers.customer_id.is_unique)

    def test_restaurant_ids_unique(self):
        self.assertTrue(self.restaurants.restaurant_id.is_unique)

    def test_foreign_keys_resolve(self):
        self.assertTrue(self.orders.customer_id.isin(self.customers.customer_id).all())
        self.assertTrue(self.orders.restaurant_id.isin(self.restaurants.restaurant_id).all())

    def test_status_values_are_expected(self):
        self.assertTrue(set(self.orders.order_status.unique()).issubset({"Delivered", "Cancelled", "Delayed"}))

    def test_amount_formula_reconciles(self):
        calculated = self.orders.order_value + self.orders.delivery_fee - self.orders.discount
        self.assertTrue(((calculated - self.orders.net_amount).abs() <= 0.011).all())

    def test_ratings_missing_for_non_delivered_orders(self):
        non_delivered = self.orders.order_status.ne("Delivered")
        self.assertTrue(self.orders.loc[non_delivered, "customer_rating"].isna().all())

    def test_item_counts_positive(self):
        self.assertTrue((self.orders.items_count > 0).all())

if __name__ == "__main__":
    unittest.main()
