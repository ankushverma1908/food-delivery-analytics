"""Validate source data and write a compact CSV quality report."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
def main():
    o=pd.read_csv(DATA/"food_delivery_orders.csv")
    c=pd.read_csv(DATA/"customers.csv")
    r=pd.read_csv(DATA/"restaurants.csv")
    checks=[
      ("Unique order IDs",o.order_id.is_unique,int(o.order_id.nunique()),"All order IDs unique"),
      ("Unique customer IDs",c.customer_id.is_unique,int(c.customer_id.nunique()),"All customer IDs unique"),
      ("Unique restaurant IDs",r.restaurant_id.is_unique,int(r.restaurant_id.nunique()),"All restaurant IDs unique"),
      ("Customer foreign keys",o.customer_id.isin(c.customer_id).all(),int((~o.customer_id.isin(c.customer_id)).sum()),"0 unmatched"),
      ("Restaurant foreign keys",o.restaurant_id.isin(r.restaurant_id).all(),int((~o.restaurant_id.isin(r.restaurant_id)).sum()),"0 unmatched"),
      ("Non-negative amounts",(o[["order_value","delivery_fee","discount","net_amount"]]>=0).all().all(),int((o[["order_value","delivery_fee","discount","net_amount"]]<0).sum().sum()),"No negative values"),
      ("Net amount formula",((o.order_value+o.delivery_fee-o.discount-o.net_amount).abs()<=0.011).all(),int(((o.order_value+o.delivery_fee-o.discount-o.net_amount).abs()>0.011).sum()),"0 mismatches"),
    ]
    report=pd.DataFrame(checks,columns=["check","passed","observed","expected"])
    out=ROOT/"reports";out.mkdir(exist_ok=True)
    report.to_csv(out/"data_quality_checks.csv",index=False)
    print(report.to_string(index=False))
if __name__=="__main__": main()
