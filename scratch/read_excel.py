import pandas as pd
import os

excel_path = os.path.join('data', 'MOTU', 'lista_MOTU.xlsx')
if os.path.exists(excel_path):
    # Cargar Excel usando la fila 1 como cabecera (indexada en 0 es la fila 1, por lo que pasamos header=1)
    df = pd.read_excel(excel_path, header=1)
    print("Columnas reales:", df.columns.tolist())
    print("\n--- REGISTROS ESPECÍFICOS ---")
    
    ids_to_check = [13977, 13978, 14038, 14039]
    # Buscar en 'Figure ID'
    if 'Figure ID' in df.columns:
        matches = df[df['Figure ID'].isin(ids_to_check)]
        print(matches[['Figure ID', 'Name', 'Image Path', 'Image URL', 'Detail Link']].to_string())
    else:
        print("No se encontró columna 'Figure ID'.")
else:
    print(f"No existe el archivo {excel_path}")
