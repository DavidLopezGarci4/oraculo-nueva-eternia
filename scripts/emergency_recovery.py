
import pandas as pd
from pathlib import Path
import os

def deep_audit_xlsx(path):
    print(f"\nDEEP AUDIT: {path}")
    try:
        xl = pd.ExcelFile(path)
        total_in_file = 0
        for sheet in xl.sheet_names:
            # Try headers from -1 (None) to 3
            for h in [None, 0, 1, 2]:
                try:
                    df = pd.read_excel(xl, sheet_name=sheet, header=h)
                    # Search every cell for "SÍ", "SI", "YES" (case insensitive)
                    # This is slow but thorough
                    # Or find col containing "Adquirido"
                    target_col = None
                    if h is None:
                        # Find which column has "Adquirido" in the first few rows
                        for col in df.columns:
                            sample = df[col].head(5).astype(str).str.upper()
                            if sample.str.contains("ADQUIRIDO").any():
                                target_col = col
                                break
                    else:
                        for col in df.columns:
                            if "ADQUIRIDO" in str(col).upper():
                                target_col = col
                                break
                    
                    if target_col is not None:
                        mask = df[target_col].astype(str).str.strip().str.upper().str.startswith('S', na=False)
                        # Filter out the header itself if it was caught in data
                        found_df = df[mask]
                        # Filter out rows where the target_col value IS "ADQUIRIDO"
                        found_df = found_df[~found_df[target_col].astype(str).str.strip().str.upper().str.contains("ADQUIRIDO")]
                        
                        count = found_df.shape[0]
                        if count > 0:
                            print(f"  [{sheet}] Col: {target_col}, Header: {h} -> {count} items")
                            # print(found_df.iloc[0]) # debug
                            file_total += count
                            total_in_file += count
                            break
                except: continue
        print(f"  Total for file: {total_in_file}")
        return total_in_file
    except Exception as e:
        print(f"  Error: {e}")
        return 0

if __name__ == "__main__":
    root = Path(".").absolute()
    grand_total = 0
    for f in root.rglob("*.xlsx"):
        if f.name.startswith("~$"): continue
        grand_total += deep_audit_xlsx(f)
    
    print(f"\nGRAND TOTAL ACROSS ALL FILES: {grand_total}")
