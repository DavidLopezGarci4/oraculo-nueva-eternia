
import pandas as pd
import os
from loguru import logger

def clean_excel_nulls(excel_path: str):
    logger.info(f"🧹 Iniciando limpieza de Nulos en Excel: {excel_path}")
    
    if not os.path.exists(excel_path):
        logger.error("Archivo no encontrado.")
        return

    # Usar ExcelWriter para guardar múltiples hojas
    with pd.ExcelFile(excel_path) as xl:
        sheet_names = xl.sheet_names
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet in sheet_names:
                # Leer hoja (header=1 según phase0_migration)
                df = pd.read_excel(xl, sheet_name=sheet, header=1)
                
                initial_count = len(df)
                
                # Eliminar filas donde 'Figure ID' es nulo
                if 'Figure ID' in df.columns:
                    df = df.dropna(subset=['Figure ID'])
                    # Adicionalmente limpiar si es texto "nan" o vacio
                    df = df[df['Figure ID'].astype(str).str.lower() != 'nan']
                    df = df[df['Figure ID'].astype(str).str.strip() != '']
                
                final_count = len(df)
                removed = initial_count - final_count
                
                # Escribir de vuelta (preservando el formato básico de pandas)
                # Nota: pandas no preserva colores/estilos del Excel original fácilmente
                df.to_writer = True
                df.to_excel(writer, sheet_name=sheet, index=False, startrow=1)
                
                logger.info(f"Hoja '{sheet}': {removed} filas eliminadas por ID Nulo.")

    logger.success("✅ Limpieza de Excel completada.")

if __name__ == "__main__":
    path = "c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/data/MOTU/lista_MOTU.xlsx"
    clean_excel_nulls(path)
