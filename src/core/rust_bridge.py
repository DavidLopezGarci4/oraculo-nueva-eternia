import subprocess
import os
from loguru import logger
from src.core.brain_engine import engine as python_engine

class SmartBridge:
    """
    Puente Inteligente 3OX para Nueva Eternia.
    Gestiona la ejecución híbrida Rust/Python con fallback automático.
    """
    def __init__(self, brain_path=None):
        if brain_path is None:
            # Ruta absoluta en el nuevo disco F:
            self.brain_path = "f:\\IT\\Laboratorio\\IT\\3OX.Ai-main\\oraculo-de-nueva-eternia\\.3ox\\target\\release\\brains.exe"
        else:
            self.brain_path = brain_path

    def match_items(self, name1, name2, ean1=None, ean2=None):
        """
        Intenta usar el motor de Rust (Turbo). 
        Si falla (bloqueo OS), conmuta al motor Python (Respaldo).
        """
        # 1. Intentar Modo Turbo (Rust)
        if os.path.exists(self.brain_path):
            try:
                cmd = [self.brain_path, "match", name1, name2]
                if ean1: cmd.append(ean1)
                if ean2: cmd.append(ean2)
                
                # Usar shell=False para mayor seguridad, pero capturando errores de acceso
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0 and "MATCH_RESULT" in result.stdout:
                    parts = result.stdout.strip().split("|")
                    logger.success("3OX.Bridge :: Modo TURBO (Rust) activo.")
                    return parts[1] == "true", float(parts[2])
            except (subprocess.SubprocessError, PermissionError) as e:
                logger.warning(f"3OX.Bridge :: Motor Rust bloqueado ({type(e).__name__}). Activando Respaldo...")
        else:
            logger.debug("3OX.Bridge :: Binario Rust no encontrado. Usando motor Python.")

        # 2. Fallback: Modo Respaldo (Python)
        is_match, score = python_engine.calculate_match(name1, name2, ean1, ean2)
        logger.info(f"3OX.Bridge :: Operando en Modo RESPALDO (Python) [Confianza: {score:.2f}]")
        return is_match, score

# Global Dispatcher
kernel = SmartBridge()
