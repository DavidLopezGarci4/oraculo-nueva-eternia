# Extensión Chrome: Oráculo de Eternia - Wallapop Connector

## Instalación en Chrome

### Pasos:

1. **Abre Chrome** y ve a `chrome://extensions/`

2. **Activa el Modo Desarrollador** (interruptor arriba a la derecha)

3. **Haz clic en "Cargar descomprimida"**

4. **Selecciona la carpeta**:
   ```
   oraculo-nueva-eternia/chrome-extension/
   ```

5. **¡Listo!** Verás el icono del Oráculo en tu barra de extensiones.

---

## Primer Uso

1. **Haz clic en el icono** de la extensión (👁️)
2. **Configura la URL del servidor**:
   - Local: `http://localhost:8000`
   - Docker: `http://tu-ip-local:8000`
3. **Configura la Clave de la Extensión**: el mismo valor que `EXTENSION_API_KEY` en el `.env` del backend (distinta de `ORACULO_API_KEY`, esta es de bajo privilegio y solo habilita el import de Wallapop)
4. **Guarda la configuración**

---

## Cómo Funciona

1. **Navega a Wallapop** y busca productos (ej: "motu origins")
2. **Aparecerá un botón dorado** en la esquina inferior derecha: "Enviar al Oráculo"
3. **El contador rojo** indica cuántos productos detectó en la página
4. **Haz clic en el botón** para enviar todos los productos al Purgatorio

---

## Fallback Automático

Si el servidor no está disponible, la extensión:
1. **Copia los datos al portapapeles** en formato compatible
2. Podrás pegarlos en `import_wallapop.bat` manualmente

---

## Notas Técnicas

- La extensión solo se activa en páginas de `wallapop.com`
- Los productos se guardan en el **Purgatorio** para revisión manual
- No requiere credenciales de Wallapop
- Funciona porque el navegador ya tiene la sesión iniciada

---

## Iconos (Opcional)

Para añadir iconos personalizados, coloca archivos PNG en:
```
chrome-extension/icons/
├── icon16.png   (16x16)
├── icon48.png   (48x48)
└── icon128.png  (128x128)
```

Sin iconos, Chrome mostrará un icono genérico.
