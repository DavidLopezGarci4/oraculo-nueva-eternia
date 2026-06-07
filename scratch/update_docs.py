import os

def update_docs():
    # 1. Update docs/MASTER_ROADMAP.md
    roadmap_path = "docs/MASTER_ROADMAP.md"
    if os.path.exists(roadmap_path):
        with open(roadmap_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        idx = text.rfind("Saneamiento de Navbar")
        if idx != -1:
            dash_idx = text.find("---", idx)
            if dash_idx != -1:
                new_phase = """  - [x] **Saneamiento de Navbar**: Eliminado el bot\u00f3n inoperante de campana de notificaciones de la barra superior.

- [x] **Phase 65: Caracter\u00edsticas Pareto 80/20 y Blindaje Wallapop (07/06/2026)**
  - [x] **Santuario Compartido (Showcase)**: Campo `is_public_showcase` en base de datos y UI con endpoint p\u00fablico seguro exento de campos financieros, con bypass de login en `/santuario/:username`.
  - [x] **Filtro Cruzado de Deseos**: Toggle "Solo Deseos" en Mercader de Eternos para cruzar ofertas de subastas con tu Lista de Deseos en tiempo real.
  - [x] **Regimientos de Completitud (Waves)**: Panel en Orbe de Grayskull que agrupa el cat\u00e1logo por sub-categor\u00edas y muestra el progreso de adquisici\u00f3n de figuras.
  - [x] **Arsenal Analytics**: Gr\u00e1fico circular Donut Chart con Recharts en Orbe de Grayskull detallando el estado de conservaci\u00f3n (MOC, New, Loose) y estimaci\u00f3n del valor de mercado ajustado.
  - [x] **Renovaci\u00f3n Local de SSL**: Script `renew_ssl.sh` local para renovaci\u00f3n segura con Docker Certbot y recarga de Nginx.
  - [x] **Scraper Wallapop Hardened**: Impersonaci\u00f3n de TLS Chrome 120 mediante `curl_cffi` para peticiones API y fallback a Playwright persistente contra bloqueos WAF.

"""
                # Remove the original "Saneamiento de Navbar" line since we replace it
                # The original line starts with "  - [x] **Saneamiento de Navbar**"
                line_start = text.rfind("  - [x] **Saneamiento de Navbar**", 0, dash_idx)
                if line_start != -1:
                    updated_text = text[:line_start] + new_phase + text[dash_idx:]
                else:
                    updated_text = text[:dash_idx] + new_phase + text[dash_idx:]
                
                with open(roadmap_path, "w", encoding="utf-8") as f:
                    f.write(updated_text)
                print("Roadmap updated successfully.")
            else:
                print("Could not find separator after target.")
        else:
            print("Could not find target in Roadmap.")
    else:
        print("Roadmap not found.")

    # 2. Update 3ox.log
    log_path = "3ox.log"
    if os.path.exists(log_path):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n2026-06-07 13:40:00 | ARCHITECT: Implemented Pareto 80/20 Features: public showcase, wishlist cross-filtering in Auctions, sub_category completitud bars in Dashboard, and condition donut chart with Recharts. Hardened Wallapop scraper using direct API with curl_cffi and Playwright persistent profile context fallback. Created renew_ssl.sh script. - [Estatus: Validado]\n")
        print("3ox.log updated successfully.")
    else:
        print("3ox.log not found.")

if __name__ == "__main__":
    update_docs()
