
import pandas as pd
from pathlib import Path

def count_excel_ids():
    excel_path = Path('data/MOTU/lista_MOTU.xlsx')
    xl = pd.ExcelFile(excel_path)
    ids = set()
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        if 'Figure ID' in df.columns:
            for val in df['Figure ID'].dropna():
                ids.add(str(val).strip())
    print(f"Total Unique Figure IDs in Excel: {len(ids)}")

if __name__ == '__main__':
    count_excel_ids()
