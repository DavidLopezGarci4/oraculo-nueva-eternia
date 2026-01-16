# Guía de Uso: Importador Manual de Wallapop

Esta guía explica cómo importar ofertas de Wallapop al Oráculo de Eternia usando el sistema de importación manual asistida.

---

## ¿Por qué es manual?

Wallapop tiene una de las protecciones anti-scraping más agresivas del mercado. Su sistema CloudFront bloquea cualquier acceso automatizado. Por ello, usamos un enfoque híbrido: **tú navegas, el Oráculo procesa**.

---

## Método 1: Script Interactivo (Recomendado)

### Pasos:

1. **Abre Wallapop** en tu navegador: [es.wallapop.com](https://es.wallapop.com)
2. **Busca** el término deseado (ej: "motu origins")
3. **Copia** los datos de cada producto que te interese en este formato:
   ```
   Nombre del producto | Precio | URL completa
   ```
   
   **Ejemplo:**
   ```
   He-Man Origins Deluxe | 25.00 | https://es.wallapop.com/item/he-man-origins-deluxe-12345
   Skeletor Masterverse | 18.50 | https://es.wallapop.com/item/skeletor-masterverse-67890
   ```

4. **Ejecuta** el script haciendo doble clic en:
   ```
   import_wallapop.bat
   ```

5. **Pega** los datos y escribe `FIN` en una línea vacía.

6. Los items aparecerán en el **Purgatorio** de la web del Oráculo.

---

## Método 2: Solo URLs

Si solo tienes las URLs (sin nombres ni precios), también funciona:

```
https://es.wallapop.com/item/he-man-origins-12345
https://es.wallapop.com/item/teela-origins-67890
https://es.wallapop.com/item/beast-man-99999
```

> ⚠️ En este caso, el precio aparecerá como 0€ y deberás actualizarlo manualmente desde el Purgatorio.

---

## Método 3: Archivo de Texto

1. Crea un archivo `wallapop_import.txt` con el formato deseado.
2. Ejecuta desde PowerShell:
   ```powershell
   $env:PYTHONPATH="."; python -c "
   import asyncio
   from src.infrastructure.scrapers.wallapop_manual_importer import WallapopManualImporter
   i = WallapopManualImporter()
   print(asyncio.run(i.import_from_file('wallapop_import.txt')))
   "
   ```

---

## Verificación

Después de importar:
1. Abre el Oráculo en tu navegador.
2. Ve a **Admin > Purgatorio**.
3. Verás los items de Wallapop listos para ser vinculados a productos del catálogo.

---

## Consejos

- **Frecuencia**: Importa 1-2 veces por semana para mantener el pulso del mercado de segunda mano.
- **Filtrado**: Solo importa items relevantes (MOTU, He-Man, etc.). No importes todo.
- **Precios**: Los precios de Wallapop son de segunda mano, úsalos como referencia de mercado, no como precio de compra objetivo.
