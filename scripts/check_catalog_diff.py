
import sqlite3
import pandas as pd
from pathlib import Path

def find_diff():
    excel_path = Path('data/MOTU/lista_MOTU.xlsx')
    db_path = Path('oraculo.db')
    
    # 1. Load Excel names
    xl = pd.ExcelFile(excel_path)
    excel_items = set()
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        if 'Name' in df.columns:
            for _, row in df.iterrows():
                name = str(row['Name']).strip()
                if name and name != 'nan':
                    excel_items.add(name)
    
    # 2. Load DB names
    conn = sqlite3.connect(db_path)
    db_products = pd.read_sql_query("SELECT name FROM products", conn)
    db_items = set(db_products['name'].str.strip())
    conn.close()
    
    missing = excel_items - db_items
    print(f"Total Unique Excel Items: {len(excel_items)}")
    print(f"Total Unique DB Items: {len(db_items)}")
    print(f"Missing in DB count: {len(missing)}")
    if missing:
        print("Missing items (first 10):")
        for m in list(missing)[:10]:
            print(f"- {m}")

if __name__ == '__main__':
    find_diff()
