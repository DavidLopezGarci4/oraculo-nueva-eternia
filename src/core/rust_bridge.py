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
        Llamada pura al motor de Rust (Turbo).
        Devuelve el resultado bruto sin interpretaciones.
        """
        # 1. Intentar Modo Turbo (Rust)
        if os.path.exists(self.brain_path):
            try:
                cmd = [self.brain_path, "match", name1, name2]
                if ean1: cmd.append(ean1)
                if ean2: cmd.append(ean2)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0 and "MATCH_RESULT" in result.stdout:
                    parts = result.stdout.strip().split("|")
                    is_match = parts[1] == "true"
                    score = float(parts[2])
                    return is_match, score, "Rust Kernel Execution"
            except Exception as e:
                logger.warning(f"3OX.Bridge :: Motor Rust falló ({type(e).__name__}). No hay fallback.")
        
        return False, 0.0, "Rust Unavailable"

# Global Dispatcher
kernel = SmartBridge()
