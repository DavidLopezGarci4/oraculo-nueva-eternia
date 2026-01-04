import os

REPLACEMENTS = {
    "from src.interfaces.web": "from src.interfaces.web",
    "import src.interfaces.web": "import src.interfaces.web",
    "from src.infrastructure.scrapers": "from src.infrastructure.scrapers",
    "import src.infrastructure.scrapers": "import src.infrastructure.scrapers",
    "from src.infrastructure.collectors": "from src.infrastructure.collectors",
    "import src.infrastructure.collectors": "import src.infrastructure.collectors",
}

def refactor_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                changed = False
                for old, new in REPLACEMENTS.items():
                    if old in new_content:
                        new_content = new_content.replace(old, new)
                        changed = True
                
                if changed:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Refactorizado: {path}")

if __name__ == "__main__":
    refactor_imports("src")
    refactor_imports("scripts")
    refactor_imports("tests")
