import pandas as pd
from pathlib import Path

excel_path = Path("data/MOTU/lista_vintage.xlsx")
if not excel_path.exists():
    print(f"Excel not found at {excel_path}")
    exit(1)

print(f"Reading {excel_path}...")
with pd.ExcelFile(excel_path) as xl:
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        matches = df[df['Name'].str.contains('Beast Man|Mer-Man|Man-at-Arms|Stratos', case=False, na=False)]
        if not matches.empty:
            print(f"\n--- Sheet: {sheet} ---")
            for _, row in matches.iterrows():
                print(f"Name: {row.get('Name')} | Figure ID: {row.get('Figure ID')} | Image URL: {row.get('Image URL')} | Image Path: {row.get('Image Path')}")
