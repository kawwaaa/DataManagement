# ...existing code...
import os
import sys
import pandas as pd
import csv
# === CHANGE THIS TO YOUR REAL FILE PATH ===
file_path = "raw_data.csv"          # or .csv
# file_path = "C:\\Users\\nimet\\Desktop\\Pairwise\\raw_data.txt"


def try_read_csv(path):
    """Detect delimiter with csv.Sniffer (fallbacks) and read robustly.

    This function attempts to detect the separator using csv.Sniffer and
    falls back to a set of common separators. It also handles the case
    where the entire header+row is read into one column (e.g.
    ['Receipt,Descrip,Qty,...']) by re-reading with a comma separator.
    """
    # Read a sample for delimiter detection
    sample = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            sample = fh.read(8192)
    except Exception:
        sample = None

    sep = None
    if sample:
        try:
            dialect = csv.Sniffer().sniff(sample)
            sep = dialect.delimiter
        except Exception:
            # quick heuristics
            for s in [",", "\t", ";", "|"]:
                if s in sample:
                    sep = s
                    break

    # Try reading using detected sep (or let pandas infer when sep is None)
    df = None
    read_kwargs = {"on_bad_lines": "skip", "engine": "python"}
    try:
        if sep:
            df = pd.read_csv(path, sep=sep, **read_kwargs)
        else:
            # let pandas try to infer the separator
            df = pd.read_csv(path, sep=None, **read_kwargs)
    except Exception:
        # fallback: try a list of common separators until we get >1 column
        for s in [",", "\t", ";", "|"]:
            try:
                tmp = pd.read_csv(path, sep=s, **read_kwargs)
                if tmp.shape[1] > 1:
                    df = tmp
                    break
            except Exception:
                continue
        if df is None:
            # last resort: whitespace separator
            df = pd.read_csv(path, sep=r"\s+", engine="python",
                             on_bad_lines="skip")

    # If pandas produced a single-column DataFrame, it's possible the
    # header row itself contains comma-separated column names. Try re-reading
    # with comma separator in that case.
    if df is not None and len(df.columns) == 1:
        col0 = str(df.columns[0])
        first_cell = None
        try:
            first_cell = df.iloc[0, 0]
        except Exception:
            first_cell = None

        if ("," in col0) or (isinstance(first_cell, str) and "," in first_cell):
            try:
                df2 = pd.read_csv(
                    path, sep=",", engine="python", on_bad_lines="skip")
                if df2.shape[1] > 1:
                    df = df2
            except Exception:
                # keep original df if re-read fails
                pass

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]
    return df


# === READ THE FILE ===
try:
    df = try_read_csv(file_path)
except Exception as e:
    print(f"ERROR reading file: {e}")
    sys.exit(1)

# === SHOW WHAT COLUMNS WE ACTUALLY HAVE (uncomment to debug) ===
print("Columns found in your file:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

# === FIX COLUMN NAMES IF NEEDED ===
required_cols = ['Receipt', 'Descrip', 'Amount', 'ZNo']
optional_cols = ['Qty', 'UnitOfMeasureName', 'UnitOfMeasureName2']

# Check for missing required columns and fail fast with a clear message
missing_required = [c for c in required_cols if c not in df.columns]
if missing_required:
    print(f"ERROR: Missing required columns: {missing_required}")
    print("Please check your input file headers and try again.")
    sys.exit(1)

# Keep only existing columns
cols_to_keep = [col for col in required_cols +
                optional_cols if col in df.columns]
df = df[cols_to_keep].copy()

# === FILL MISSING QTY (if not present, assume 1) ===
if 'Qty' not in df.columns:
    df['Qty'] = 1
else:
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(1)

# === CLEAN TEXT / NUMERIC COLUMNS ===
df['Receipt'] = df['Receipt'].astype(str).str.strip()
df['ZNo'] = df['ZNo'].fillna('').astype(
    str).str.strip()      # keep empty if missing
df['Descrip'] = df['Descrip'].astype(str).str.strip()
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

# === CREATE UNIQUE BILL ID: Receipt + optional _Z + ZNo ===
# If ZNo is empty, don't add the "_Z" suffix.
df['unique_bill_id'] = df['Receipt'] + \
    df['ZNo'].apply(lambda z: f"_Z{z}" if z != '' else '')

# === FINAL CLEAN DATASET ===
final_df = df[[
    'unique_bill_id',
    'Receipt',
    'ZNo',
    'Descrip',
    'Qty',
    'Amount'
]].copy()

# Remove any duplicates
final_df = final_df.drop_duplicates()

# === SAVE ===
out_file = os.path.splitext(
    file_path)[0] + "_CLEAN_TRANSACTIONS_READY_FOR_APRIORI.csv"
final_df.to_csv(out_file, index=False)

print("\nSUCCESS! Clean dataset created!")
print(f"Saved to: {out_file}")
print(f"Total transactions (rows): {len(final_df)}")
print(
    f"Total REAL bills (unique bill ids): {final_df['unique_bill_id'].nunique()}")
print("\nSample of real bills:")

# Show first 3 real bills
for bill_id in final_df['unique_bill_id'].unique()[:3]:
    bill = final_df[final_df['unique_bill_id'] == bill_id]
    print(f"\n{bill_id} ({len(bill)} items)")
    print(bill[['Descrip', 'Qty', 'Amount']].to_string(index=False))
# ...existing code...
