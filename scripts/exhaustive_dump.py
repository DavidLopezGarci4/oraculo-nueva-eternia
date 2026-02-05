
import pandas as pd
from pathlib import Path
import os

def exhaustive_dump(path):
    print(f"\n--- DUMPING: {path} ---")
    if not os.path.exists(path): return
    try:
        xl = pd.ExcelFile(path)
        all_matches = []
        for sheet in xl.sheet_names:
            for h in [None, 0, 1]:
                try:
                    df = pd.read_excel(xl, sheet_name=sheet, header=h)
                    # Convert whole DF to string and check for SI/SÍ
                    # This is very broad but safe
                    for idx, row in df.iterrows():
                        row_str = row.astype(str).str.upper().tolist()
                        if any(s in ["SÍ", "SI", "YES", "TRUE", "S"] for s in row_str):
                            # Special check: avoid catching the word "SERIES" or "SIDE"
                            # We want to see if a specific cell matches exactly
                            match = False
                            for cell in row.astype(str).tolist():
                                c_up = cell.strip().upper()
                                if c_up in ["SÍ", "SI", "YES", "S", "TRUE", "1", "1.0"]:
                                    match = True
                                    break
                            if match:
                                all_matches.append((sheet, row.get('Name', 'Unknown'), row.get('Figure ID', 'N/A')))
                except: continue
        
        # Deduplicate matches
        unique_matches = list(set(all_matches))
        print(f"  Unique acquired items found: {len(unique_matches)}")
        for m in unique_matches[:10]:
            print(f"  - {m}")
        return len(unique_matches)
    except Exception as e:
        print(f"  Error: {e}")
        return 0

if __name__ == "__main__":
    root = Path(".").absolute()
    for f in root.rglob("*.xlsx"):
        if f.name.startswith("~$"): continue
        exhaustive_dump(f)
