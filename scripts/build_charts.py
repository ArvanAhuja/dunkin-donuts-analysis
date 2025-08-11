import io, os, sys, requests
import pandas as pd
import matplotlib.pyplot as plt

# === Your published Google Sheets CSV link ===
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkdOz6NFExg8W1QAsAGPmJuZza1G73f2JtdJLa_6KHaa4RQMmQhGjF_8Sotejrfl1FxIG7kcxlslc3/pub?output=csv"

# Make output folder
os.makedirs("figs", exist_ok=True)

# Download CSV
r = requests.get(CSV_URL, timeout=30)
r.raise_for_status()
csv_text = r.text

# Read CSV
df = pd.read_csv(io.StringIO(csv_text))

# ---- Robust column matching (handles typos like "Dozens of Donu") ----
def norm(s: str) -> str:
    return str(s).strip().lower().replace("  ", " ").replace("’", "'")

cols_norm = {norm(c): c for c in df.columns.tolist()}

def pick(*candidates):
    for cand in candidates:
        key = norm(cand)
        if key in cols_norm:
            return cols_norm[key]
        for k, original in cols_norm.items():
            if key in k:
                return original
    return None

date_col   = pick("date distributed", "date")
dozens_col = pick("dozens of donuts", "dozens of donut", "dozens")
price_col  = pick("prices", "total price", "total", "amount")

missing = [name for name, col in [
    ("Date", date_col), ("Dozens", dozens_col), ("TotalPrice", price_col)
] if col is None]
if missing:
    print("ERROR: Missing required column(s):", ", ".join(missing))
    print("Sheet columns:", df.columns.tolist())
    sys.exit(1)

# Rename to clean internal names
df = df.rename(columns={date_col: "Date", dozens_col: "Dozens", price_col: "TotalPrice"})

# Clean types & sort
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
df["Dozens"] = pd.to_numeric(df["Dozens"], errors="coerce")
df["TotalPrice"] = pd.to_numeric(df["TotalPrice"], errors="coerce")
df = df.dropna(subset=["Dozens", "TotalPrice"])

# Derived metrics
df["PricePerDozen"] = df["TotalPrice"] / df["Dozens"]
df["PricePerDonut"] = df["TotalPrice"] / (df["Dozens"] * 12)

# Debug (shows in Actions logs, helpful if anything breaks)
print("Columns:", df.columns.tolist())
print(df.head().to_string(index=False))

# === Charts ===

# A) Dozens over time
plt.figure()
plt.plot(df["Date"], df["Dozens"], marker="o")
plt.title("Dozens Distributed Over Time")
plt.xlabel("Date"); plt.ylabel("Dozens")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/dozens_over_time.png", dpi=160)

# B) Daily total price
plt.figure()
plt.plot(df["Date"], df["TotalPrice"], marker="o")
plt.title("Daily Total Price Over Time")
plt.xlabel("Date"); plt.ylabel("USD")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/total_price_over_time.png", dpi=160)

# C) Cumulative (running) total
plt.figure()
cum = df["TotalPrice"].cumsum()
plt.plot(df["Date"], cum, marker="o")
plt.title("Cumulative Total Revenue")
plt.xlabel("Date"); plt.ylabel("USD (running total)")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/cumulative_total.png", dpi=160)

# D) Price per dozen
plt.figure()
plt.plot(df["Date"], df["PricePerDozen"], marker="o")
plt.title("Price per Dozen")
plt.xlabel("Date"); plt.ylabel("USD per dozen")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("figs/price_per_dozen.png", dpi=160)

print("Charts saved in figs/ 🎉")

