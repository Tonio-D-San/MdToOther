import importlib
import subprocess
import sys

def ask_yes_no(prompt):
    while True:
        choice = input(f"{prompt} [Y/N]: ").strip().lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Per favore rispondi Y (sì) o N (no).")

def install_missing_packages():
    from pathlib import Path
    import urllib.request
    yes_no = True
    for package in ["pypandoc", "plantuml", "six"]:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"Libreria mancante: {package}.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    librsvg_installed = False
    # try:
    #     result = subprocess.run(
    #         ["conda", "list", "librsvg"],
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text=True,
    #         check=True
    #     )
    #     if "librsvg" in result.stdout:
    #         librsvg_installed = True
    #         print("librsvg già installato con conda.")
    # except subprocess.CalledProcessError:
    #     pass

    if not librsvg_installed:
        print("📦 librsvg non trovato.")
        yes_no = ask_yes_no("Vuoi installare librsvg via conda?")
        if yes_no:
            try:
                subprocess.check_call(
                    ["conda", "install", "-y", "-c", "conda-forge", "librsvg"]
                )
                print("librsvg installato con successo via conda.\n")
            except subprocess.CalledProcessError:
                print("⚠️ Impossibile installare librsvg via conda. Installalo manualmente.")
        else:
            print("⚠️ librsvg non installato. Installare manualmente tramite 'conda install librsvg'")

    jar_dir = Path(__file__).parent / "lib"
    jar_dir.mkdir(exist_ok=True)
    jar_path = jar_dir / "plantuml.jar"

    if not jar_path.exists():
        print(f"🔍 plantuml.jar non trovato in {jar_path}")
        if ask_yes_no("Vuoi scaricare automaticamente l’ultima versione di PlantUML?"):
            try:
                url = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
                print(f"Download in corso da {url}...")
                urllib.request.urlretrieve(url, jar_path)
                print(f"plantuml.jar scaricato correttamente in {jar_path}\n")
            except Exception as e:
                print(f"Errore durante il download: {e}")
                print("Scaricalo manualmente da: https://plantuml.com/download")
        else:
            print("plantuml.jar non scaricato.")
    else:
        print(f"plantuml.jar già presente in {jar_path}")
    return yes_no

def __init__():
    install_missing_packages()