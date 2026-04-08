# smart_pair_apriori.py
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import json
from datetime import datetime

file_path = "raw_data_cleaned.csv"

print("Loading data...")
df = pd.read_csv(file_path)

# CLEAN DATA
df['Descrip'] = df['Descrip'].fillna('').astype(str).str.strip()
df = df[df['Descrip'] != '']

# REMOVE ALL VEG PRODUCTS
print("Removing all products starting with 'VEG'...")
df = df[~df['Descrip'].str.upper().str.startswith('VEG')]
print(f"Rows after removing VEG items: {len(df)}")

# ENSURE PRICE & QUANTITY ARE NUMERIC
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
df['total_value'] = df['Amount'] * df['Qty']

print(f"Total bills: {df['unique_bill_id'].nunique()}")

# STEP 1: FIND TOP 10 BEST-SELLING PRODUCTS BY REVENUE
print("\nFinding Top 10 best-selling products by revenue...")
top_products_df = (
    df.groupby('Descrip')['total_value']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

top_10_products = top_products_df.index.tolist()
print("TOP 10 BEST-SELLING PRODUCTS:")
for i, (prod, revenue) in enumerate(top_products_df.items(), 1):
    print(f" {i:2}. {prod[:50]:<50} → LKR {revenue:,.0f}")

# STEP 2: FILTER BILLS THAT CONTAIN AT LEAST ONE TOP 10 PRODUCT
print(f"\nFiltering bills containing at least one of the Top 10 products...")
bills_with_top10 = df[df['Descrip'].isin(
    top_10_products)]['unique_bill_id'].unique()
filtered_df = df[df['unique_bill_id'].isin(bills_with_top10)]

print(f"Bills with Top 10 products: {len(bills_with_top10)}")

# BUILD BASKETS (only from relevant bills)
baskets = (
    filtered_df.groupby('unique_bill_id')['Descrip']
    .apply(lambda x: [str(s).strip() for s in x.tolist() if str(s).strip()])
    .tolist()
)

print(f"Final baskets for Apriori: {len(baskets)}")

# ONE-HOT ENCODE
te = TransactionEncoder()
te_ary = te.fit(baskets).transform(baskets)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

print("Running Apriori on Top 10 product context...")
frequent_itemsets = apriori(
    df_encoded, min_support=0.005, use_colnames=True, max_len=3)

if frequent_itemsets.empty:
    print("No frequent itemsets found.")
    exit()

rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.5)

# KEEP ONLY PAIRS
rules = rules[rules['antecedents'].apply(len) == 1]
rules = rules[rules['consequents'].apply(len) == 1]
rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x)[0])
rules['consequents'] = rules['consequents'].apply(lambda x: list(x)[0])

# REMOVE SELF-BUNDLING
rules = rules[rules['antecedents'] != rules['consequents']]

# REMOVE DUPLICATE PAIRS (keep stronger direction)
seen_pairs = set()
clean_rules = []
for _, row in rules.iterrows():
    pair = tuple(sorted([row['antecedents'], row['consequents']]))
    if pair not in seen_pairs:
        seen_pairs.add(pair)
        clean_rules.append(row)

rules = pd.DataFrame(clean_rules)
rules = rules.sort_values(['lift', 'confidence'], ascending=[False, False])

# STEP 3: FOR EACH TOP 10 PRODUCT → FIND BEST BUNDLE PARTNER
print("\nFinding best bundle partner for each Top 10 product...")
final_bundles = []

for product in top_10_products:
    # Look for rules where this product is antecedent OR consequent
    candidates = rules[
        (rules['antecedents'] == product) |
        (rules['consequents'] == product)
    ].head(3)  # top 3 candidates

    best = None
    for _, row in candidates.iterrows():
        partner = row['consequents'] if row['antecedents'] == product else row['antecedents']
        # Skip if partner is also in top 10? No — we want cross-sell!
        best = {
            "top_product": product,
            "bundle_with": partner,
            "confidence": round(row['confidence'] * 100, 1),
            "lift": round(row['lift'], 1),
            "direction": "→" if row['antecedents'] == product else "←"
        }
        break  # take strongest

    if not best:
        best = {
            "top_product": product,
            "bundle_with": "No strong partner found",
            "confidence": 0,
            "lift": 0,
            "direction": ""
        }
    final_bundles.append(best)

# SAVE RESULT
result = {
    "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "top_10_products_by_revenue": [
        {"rank": i+1, "product": p,
            "revenue_lkr": int(top_products_df.iloc[i])}
        for i, p in enumerate(top_10_products)
    ],
    "total_relevant_bills": len(bills_with_top10),
    "smart_bundles_for_top10": final_bundles
}

with open("smart_pairs_for_app.json", "w", encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

# PRINT FINAL OUTPUT
print("\n" + "="*100)
print("FINAL RESULT: BEST BUNDLE PARTNERS FOR TOP 10 PRODUCTS")
print("="*100)
for b in final_bundles:
    arrow = b['direction']
    print(f"{b['top_product'][:50]:<50} {arrow} {b['bundle_with'][:50]:<50}")
    print(f"    {b['confidence']:5.1f}% chance | Lift: {b['lift']:4.1f}x")
    print("-" * 90)

print(f"\nSUCCESS! Results saved to smart_pairs_for_app.json")
print("Your app now shows: Top 10 + Their Best Bundle Partners")
