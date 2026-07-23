# 🍔 Food Delivery Analytics (Swiggy/Zomato-style)

Order-level analysis of a food delivery platform, covering revenue trends, customer
behavior (RFM segmentation), restaurant/cuisine performance, delivery-time analysis,
and city-wise insights — the kind of analysis a data analyst would run for a
Swiggy/Zomato-style business.

## 📊 What's inside

- **Revenue & order trends** — monthly revenue, order volume, hour-of-day and
  day-of-week demand patterns
- **Customer behavior** — repeat purchase rate, average lifetime spend, and an
  RFM (Recency, Frequency, Monetary) segmentation into Champions / Loyal /
  Potential / At Risk cohorts
- **Restaurant & cuisine performance** — top-performing cuisines and restaurants by
  revenue
- **Delivery performance** — delivery time distribution, cancellation/delay rates,
  and their link to customer ratings
- **City-wise insights** — revenue and delivery speed broken down by city

## 🗂️ Project structure

```
food-delivery-analytics/
├── data/
│   ├── generate_data.py       # generates the synthetic dataset
│   ├── food_delivery_orders.csv
│   ├── customers.csv
│   └── restaurants.csv
├── notebooks/
│   └── food_delivery_analysis.ipynb
├── requirements.txt
└── README.md
```

## 📦 Dataset

The dataset (~15,000 orders, 2,500 customers, 180 restaurants across 7 Indian
cities) is **synthetically generated** with realistic distributions (order values,
delivery times, ratings, cancellations) to resemble a real Swiggy/Zomato export —
no real user data is used. Regenerate it anytime with:

```bash
cd data
python generate_data.py
```

Swap in a real order export with the same column names and the notebook works
unchanged.

## 🚀 Getting started

```bash
git clone https://github.com/ankushverma1908/food-delivery-analytics.git
cd food-delivery-analytics
pip install -r requirements.txt
jupyter notebook notebooks/food_delivery_analysis.ipynb
```

## 🔑 Key takeaways

- Weekend evenings (Fri–Sun, 7–10 PM) show the highest order density — a signal
  for staffing and promo timing
- RFM segmentation surfaces **Champions** and **At Risk** cohorts for targeted
  retention campaigns
- A small set of cuisines/restaurants drives a disproportionate share of revenue
- Delivery delays correlate with lower ratings — a clear lever for retention

## 🛠️ Tech stack

Python · pandas · NumPy · Matplotlib · Seaborn · Jupyter

## 📄 License

MIT
