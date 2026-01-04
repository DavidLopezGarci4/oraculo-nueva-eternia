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
        Si falla o tiene poca confianza, usa el motor Python (Respaldo inteligente).
        """
        rust_match = None
        rust_score = 0.0

        # 1. Intentar Modo Turbo (Rust)
        if os.path.exists(self.brain_path):
            try:
                cmd = [self.brain_path, "match", name1, name2]
                if ean1: cmd.append(ean1)
                if ean2: cmd.append(ean2)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if result.returncode == 0 and "MATCH_RESULT" in result.stdout:
                    parts = result.stdout.strip().split("|")
                    rust_match = parts[1] == "true"
                    rust_score = float(parts[2])
                    
                    # Si Rust detecta un match perfecto, lo aceptamos de inmediato
                    if rust_match and rust_score >= 0.95:
                        logger.success("3OX.Bridge :: Modo TURBO (Rust) - Match Perfecto.")
                        return True, rust_score, "Rust Turbo Match"
            except Exception as e:
                logger.warning(f"3OX.Bridge :: Motor Rust omitido ({type(e).__name__}).")

        # 2. Respaldo Inteligente (Python con RapidFuzz)
        py_match, py_score, py_reason = python_engine.calculate_match(name1, name2, ean1, ean2)
        
        # Lógica de Decisión: 
        # Si Python tiene un score significativamente mejor que Rust, preferimos Python.
        if py_score > rust_score:
            logger.info(f"3OX.Bridge :: Usando REFUERZO Python (RapidFuzz) [Score: {py_score:.2f} | Reason: {py_reason}]")
            return py_match, py_score, py_reason
        else:
            logger.info(f"3OX.Bridge :: Manteniendo resultado Rust [Score: {rust_score:.2f}]")
            return rust_match if rust_match is not None else False, rust_score, "Rust Match (Fallback)"

# Global Dispatcher
kernel = SmartBridge()
