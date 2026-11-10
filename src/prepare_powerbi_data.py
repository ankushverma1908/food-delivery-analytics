"""Export source CSVs into Power BI fact and dimension tables."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
OUT=DATA/"processed"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    orders=pd.read_csv(DATA/"food_delivery_orders.csv",parse_dates=["order_date"])
    customers=pd.read_csv(DATA/"customers.csv",parse_dates=["signup_date"])
    restaurants=pd.read_csv(DATA/"restaurants.csv")
    dates=pd.date_range(orders.order_date.min().normalize(),orders.order_date.max().normalize(),freq="D")
    dim_date=pd.DataFrame({"Date":dates})
    dim_date["DateKey"]=dim_date.Date.dt.strftime("%Y%m%d").astype("int64")
    dim_date["Year"]=dim_date.Date.dt.year
    dim_date["Quarter"]="Q"+dim_date.Date.dt.quarter.astype(str)
    dim_date["MonthNo"]=dim_date.Date.dt.month
    dim_date["MonthName"]=dim_date.Date.dt.month_name()
    dim_date["YearMonth"]=dim_date.Date.dt.strftime("%Y-%m")
    dim_date["DayName"]=dim_date.Date.dt.day_name()
    dim_date["WeekdayNo"]=dim_date.Date.dt.dayofweek+1
    dim_date["IsWeekend"]=dim_date.Date.dt.dayofweek>=5
    fact=orders.copy()
    fact["DateKey"]=fact.order_date.dt.strftime("%Y%m%d").astype("int64")
    fact["OrderHour"]=fact.order_date.dt.hour
    fact["IsWeekend"]=fact.order_date.dt.dayofweek>=5
    fact.to_csv(OUT/"FactOrders.csv",index=False)
    customers.to_csv(OUT/"DimCustomer.csv",index=False)
    restaurants.to_csv(OUT/"DimRestaurant.csv",index=False)
    dim_date.to_csv(OUT/"DimDate.csv",index=False)
    print("Exported FactOrders, DimCustomer, DimRestaurant, DimDate to data/processed/")
if __name__=="__main__": main()
