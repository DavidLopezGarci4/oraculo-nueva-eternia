import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

def main():
    print("==========================================")
    print("🧹 PURIFICACIÓN Y COMPACTACIÓN DEL ORÁCULO")
    print("==========================================")
    
    from src.infrastructure.database_cloud import SessionCloud
    from src.application.services.maintenance_service import MaintenanceService
    
    print("\nIniciando mantenimiento FinOps...")
    
    try:
        with SessionCloud() as db:
            stats = MaintenanceService.compact_database(db)
            
        print("\n✅ Mantenimiento completado con éxito!")
        print("------------------------------------------")
        print(f"  Productos Procesados:    {stats.get('products_processed', 0)}")
        print(f"  Estadísticas Mensuales:  {stats.get('monthly_stats_saved', 0)} creadas/actualizadas")
        print(f"  Ofertas Purgadas:        {stats.get('offers_purged', 0)} obsoletas eliminadas")
        print(f"  Historial de Precios:    {stats.get('price_history_purged', 0)} filas detalladas limpiadas")
        print(f"  Logs Truncados:          {stats.get('logs_truncated', 0)} registros antiguos")
        print(f"  Lista Negra Limpiada:    {stats.get('blacklist_purged', 0)} descartes viejos")
        print("------------------------------------------")
        print("¡Base de datos equilibrada y optimizada!")
        
    except Exception as e:
        print(f"\n❌ Error fatal durante el mantenimiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
