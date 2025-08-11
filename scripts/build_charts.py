import io, os, requests
import pandas as pd
import matplotlib.pyplot as plt

# 1) Your published Google Sheets CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkdOz6NFExg8W1QAsAGPmJuZza1G73f2JtdJLa_6KHaa4RQMmQhGjF_8Sotejrfl1FxIG7kcxlslc3/pub?output=csv"

# 2) Create output folder for charts
os.makedirs("figs", exist_ok=True)

# 3) Download CSV from Google
r = requests.get(CSV_URL, timeout=30)
r.raise_for_status()
csv_text = r.text

# 4) Read CSV into a table
df = pd.read_csv(io.StringIO(csv_text))

# 5) Clean column names (based on your screenshot)
rename_map = {}
for col in df.columns:
    low = col.lower()
    if "date" in low:
        rename_map[col] = "Date"
    elif "dozen" in low:
        rename_map[col] = "Dozens"
    elif "price" in low:
        rename_map[col] = "TotalPrice"
df = df.rename(columns=rename_map)

# 6) Parse/sort dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date")

# 7) Extra metrics
df["PricePerDozen"] = df["TotalPrice"] / df["Dozens"]
df["PricePerDonut"] = df["TotalPrice"] / (df["Dozens"] * 12)
df["CumulativeTotal"] = df["TotalPrice"].cumsum()

# 8) Charts → saved as PNGs in figs/
plt.figure()
plt.plot(df["Date"], df["Dozens"], marker="o")
plt.title("Dozens Distributed Over Time")
plt.xlabel("Date"); plt.ylabel("Dozens")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/dozens_over_time.png", dpi=160)

plt.figure()
plt.plot(df["Date"], df["CumulativeTotal"], marker="o")
plt.title("Cumulative Total Revenue")
plt.xlabel("Date"); plt.ylabel("USD (running total)")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/total_price_over_time.png", dpi=160)

plt.figure()
plt.plot(df["Date"], df["PricePerDozen"], marker="o")
plt.title("Price per Dozen")
plt.xlabel("Date"); plt.ylabel("USD per dozen")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/price_per_dozen.png", dpi=160)

print("Charts saved in figs/ 🎉")
