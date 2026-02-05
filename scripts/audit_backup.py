
import pandas as pd
from pathlib import Path
import os

def exhaustive_search(path_to_file):
    print(f"--- Exhaustive Audit: {path_to_file} ---")
    if not os.path.exists(path_to_file):
        print("  File not found.")
        return
    
    try:
        xl = pd.ExcelFile(path_to_file)
        file_total = 0
        for sheet in xl.sheet_names:
            # Try multiple headers
            for h in [1, 0, 2]:
                try:
                    df = pd.read_excel(xl, sheet_name=sheet, header=h)
                    # Check ANY column for SÍ/SI
                    # We look for a column that has "Adquirido" in its name
                    acq_col = None
                    for col in df.columns:
                        if "ADQUIRIDO" in str(col).upper():
                            acq_col = col
                            break
                    
                    if acq_col is not None:
                        mask = df[acq_col].astype(str).str.strip().str.upper().str.startswith('S', na=False)
                        count = df[mask].shape[0]
                        if count > 0:
                            print(f"  [{sheet}] Col: {acq_col}, Header: {h} -> {count} items")
                            file_total += count
                            # Print a few to be sure
                            # print(df[mask][['Name', acq_col]].head(2))
                            break
                except: continue
        print(f"  FILE GRAND TOTAL: {file_total}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    root = Path(".").absolute()
    files = [
        root / "data" / "MOTU" / "lista_MOTU_backup.xlsx",
        root / "src" / "data" / "MOTU" / "lista_MOTU_backup.xlsx"
    ]
    for f in files:
        exhaustive_search(f)
