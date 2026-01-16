// Popup script para la extensión del Oráculo

document.addEventListener('DOMContentLoaded', async () => {
    const serverUrlInput = document.getElementById('serverUrl');
    const saveBtn = document.getElementById('saveBtn');
    const statusDiv = document.getElementById('status');

    // Cargar configuración guardada
    const config = await chrome.storage.sync.get(['serverUrl']);
    serverUrlInput.value = config.serverUrl || 'http://localhost:8000';

    // Guardar configuración
    saveBtn.addEventListener('click', async () => {
        const serverUrl = serverUrlInput.value.trim();

        if (!serverUrl) {
            showStatus('Por favor, introduce una URL válida', 'error');
            return;
        }

        // Guardar en storage
        await chrome.storage.sync.set({ serverUrl: serverUrl });

        // Verificar conexión
        try {
            const response = await fetch(`${serverUrl}/api/health`, {
                method: 'GET',
                mode: 'cors'
            });

            if (response.ok) {
                showStatus('✅ Configuración guardada. Conexión OK.', 'success');
            } else {
                showStatus('⚠️ Guardado, pero el servidor no responde.', 'error');
            }
        } catch (error) {
            showStatus('💾 Guardado. Verifica que el Oráculo esté activo.', 'error');
        }
    });

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';

        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
});
