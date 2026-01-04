import os

REPLACEMENTS = {
    'src/application/jobs': 'src/application/jobs',
    'from src.application.jobs': 'from src.application.jobs',
    'import src.application.jobs': 'import src.application.jobs'
}

def refactor(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.yml')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    new_content = content
                    changed = False
                    for old, new in REPLACEMENTS.items():
                        if old in new_content:
                            new_content = new_content.replace(old, new)
                            changed = True
                    
                    if changed:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Refactorizado: {path}")
                except Exception as e:
                    print(f"Error en {path}: {e}")

if __name__ == "__main__":
    refactor('src')
    refactor('.github')
    refactor('scripts')
