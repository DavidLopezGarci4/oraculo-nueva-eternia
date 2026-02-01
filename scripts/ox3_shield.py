import sys
import io

def apply_3ox_shield():
    """
    Garantiza que la salida de consola sea UTF-8 para evitar corrupcin de datos
    y errores de caracteres no reconocidos en Windows/Docker.
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if __name__ == "__main__":
    apply_3ox_shield()
    print("🛡️ 3OX Shield: Unicode protection active. Output is now UTF-8.")
