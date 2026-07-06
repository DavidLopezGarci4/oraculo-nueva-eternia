import sys
import subprocess

def check_pkgs():
    print("Python executable:", sys.executable)
    # Run pip list
    res = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print(res.stdout)

if __name__ == "__main__":
    check_pkgs()
