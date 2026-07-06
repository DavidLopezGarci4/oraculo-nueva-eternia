from src.interfaces.api.deps import ensure_scrapers_registered

print("Executing ensure_scrapers_registered()...")
try:
    ensure_scrapers_registered()
    print("Execution completed successfully!")
except Exception as e:
    print(f"Error during registration: {e}")
