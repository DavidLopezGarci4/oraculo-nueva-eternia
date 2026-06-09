import os
import re

path = "docs/DOCUMENTACION_MAESTRA.md"

if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Clean up double-encoded UTF-8 characters
    content = content.replace("MÃ³dulo", "Módulo")
    content = content.replace("mÃ³dulo", "módulo")
    content = content.replace("menÃº", "menú")
    content = content.replace("cÃ³digo", "código")
    
    # Clean up "Teoría" variations
    content = content.replace("TeorÃ­a", "Teoría")
    content = content.replace("Teor\xada", "Teoría")
    content = content.replace("Teor\xada", "Teoría")
    
    # Clean up standard single-encoded invalid chars (e.g. from cp1252/latin1 leftovers)
    content = content.replace("Normalizaci\ufffdn", "Normalización")
    content = content.replace("Calibraci\ufffdn", "Calibración")
    content = content.replace("versi\ufffdn", "versión")
    content = content.replace("Or\ufffdculo", "Oráculo")
    content = content.replace("par\ufffdmetros", "parámetros")
    content = content.replace("funci\ufffdn", "función")
    content = content.replace("exclusi\ufffdn", "exclusión")
    content = content.replace("l\ufffdnea", "línea")
    content = content.replace("c\ufffddigo", "código")
    content = content.replace("a\ufffddido", "añadido")
    content = content.replace("empu\ufffadura", "empuñadura")
    content = content.replace("p\ufffdginas", "páginas")
    content = content.replace("m\ufffdviles", "móviles")
    content = content.replace("pose\ufffddas", "poseídas")
    content = content.replace("tem\ufffdtico", "temático")
    content = content.replace("ordenaci\ufffdn", "ordenación")

    # 1. Update variables table
    target_table = "| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |"
    replacement_table = (
        "| `SUPABASE_DATABASE_URL` | Connection string a la base de datos maestra en la nube. | Requerida (Cloud) |\n"
        "| `IMAGE_CACHE_DIR` | Directorio local donde se guardarán las imágenes de productos (caché local). Por defecto data/image_cache. | Opcional |"
    )
    if target_table in content:
        content = content.replace(target_table, replacement_table)
        print("Updated variables table in DOCUMENTACION_MAESTRA.md")
    else:
        print("Warning: Target variables table not found!")

    # 2. Update Notes for the Future
    target_notes = (
        "- **Módulo Radar P2P**: El módulo Radar P2P ha sido desactivado del menú principal del frontend ya que "
        "actuaba como un visor independiente de oportunidades P2P (Teoría de Cuarentena P25) y no se le estaba dando "
        "uso continuo. El código subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece "
        "en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React."
    )
    
    replacement_notes = (
        "- **Módulo Radar P2P**: El módulo Radar P2P ha sido desactivado del menú principal del frontend ya que "
        "actuaba como un visor independiente de oportunidades P2P (Teoría de Cuarentena P25) y no se le estaba dando "
        "uso continuo. El código subyacente (`RadarP2P.tsx` y endpoint `/api/radar/p2p-opportunities`) permanece "
        "en el proyecto por si se desea reactivar en el futuro, pero no interfiere con el flujo principal ni el enrutado de React.\n"
        "- **Caché Local de Imágenes**: Para mejorar el rendimiento, el sistema cuenta con un caché local de imágenes (Phase 68) "
        "que se sirve a través de FastAPI en `/api/static/images`. Si se activa `use_local_images` en el frontend, se cargan "
        "estas imágenes locales con fallback automático en error al hotlink de origen."
    )

    if target_notes in content:
        content = content.replace(target_notes, replacement_notes)
        print("Updated Notes for the Future in DOCUMENTACION_MAESTRA.md")
    else:
        # Let's search by a simpler prefix to be robust
        prefix = "- **Módulo Radar P2P**:"
        if prefix in content:
            # Let's locate the line starting with prefix and replace the entire line
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if line.strip().startswith(prefix):
                    lines[idx] = replacement_notes
                    content = "\n".join(lines)
                    print("Updated Notes for the Future (prefix match) in DOCUMENTACION_MAESTRA.md")
                    break
        else:
            print("Warning: Target notes section not found!")

    # Write back as clean UTF-8
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("DOCUMENTACION_MAESTRA.md rewritten as clean UTF-8.")
else:
    print("Error: DOCUMENTACION_MAESTRA.md not found.")
