import importlib
import subprocess
import sys

REQUIRED_LIBRARIES = [
    "pypandoc",
    "plantuml",
    "librsvg"
]

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
    yes_no = True
    for package in ["pypandoc", "plantuml"]:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"📦 Libreria mancante: {package}.")
            if ask_yes_no(f"Vuoi installare {package}?"):
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installata con successo.\n")
            else:
                print(f"⚠️ {package} non installata.\n")

    librsvg_installed = False
    try:
        result = subprocess.run(
            ["conda", "list", "librsvg"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if "librsvg" in result.stdout:
            librsvg_installed = True
            print("✅ librsvg già installato con conda.")
    except subprocess.CalledProcessError:
        pass

    if not librsvg_installed:
        print("📦 librsvg non trovato.")
        yes_no = ask_yes_no("Vuoi installare librsvg via conda?")
        if yes_no:
            try:
                subprocess.check_call(
                    ["conda", "install", "-y", "-c", "conda-forge", "librsvg"]
                )
                print("✅ librsvg installato con successo via conda.\n")
            except subprocess.CalledProcessError:
                print("⚠️ Impossibile installare librsvg via conda. Installalo manualmente.")
        else:
            print("⚠️ librsvg non installato. Installare manualmente tramite 'conda install librsvg'")
    return yes_no

def __init__():
    install_missing_packages()