import subprocess, os

def snake_to_pascal(snake_str: str) -> str:
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def paths_from_input():
    import argparse

    parser = argparse.ArgumentParser(description="Inserisci immagini/snippet e converti in DOCX.")
    parser.add_argument("file", help="Nome del file markdown")

    input_file = parser.parse_args().file

    if not os.path.splitext(input_file)[1]:
        input_file += ".md"

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    title_case = snake_to_pascal(base_name)

    default_input = os.path.join("", title_case, base_name + os.path.splitext(input_file)[1])
    if not os.path.exists(default_input):
        raise FileNotFoundError(f"File non trovato: {default_input}")

    return (
        default_input,
        base_name,
        os.path.join("", title_case, "immagini"),
        os.path.join("", title_case, "snippets"),
        os.path.join("", title_case, f"{base_name}_output")
    )

def process_puml_local(puml_path, svg_path):
    from pathlib import Path
    jar_path = Path(__file__).parent / "lib" / "plantuml.jar"
    if not jar_path.exists():
        print(f"plantuml.jar non trovato in {jar_path}")
        return False

    out_dir = os.path.dirname(svg_path)
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "java", "-jar", str(jar_path),
        "-tsvg", "-o", out_dir, puml_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ (Locale) {puml_path} → {svg_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Errore locale su {puml_path}: {e}")
        return False

def process_puml(puml_path, svg_path, max_retries=3, retry_delay=2):
    from plantuml import PlantUML, PlantUMLHTTPError
    import time
    server = PlantUML(url='https://www.plantuml.com/plantuml/svg/')

    os.makedirs(os.path.dirname(svg_path), exist_ok=True)

    for attempt in range(1, max_retries + 1):
        try:
            result = server.processes_file(puml_path, outfile=svg_path)
            if result:
                print(f"✅ (Online) {svg_path} generato!")
                return True
            else:
                print(f"⚠️ Errore: {puml_path} non generato correttamente (online)")
                return False

        except PlantUMLHTTPError as e:
            print(f"⚠️ Tentativo {attempt}/{max_retries} fallito ({type(e).__name__}): {e}")
            if attempt < max_retries:
                print("↻ Riprovo...")
                time.sleep(retry_delay)
            else:
                print("Tutti i tentativi online falliti, passo alla modalità locale...")
                return process_puml_local(puml_path, svg_path)

        except Exception as e:
            msg = str(e)
            print(f"⚠️ Errore generico: {msg}")
            if "HTTP" in msg or "Connection" in msg:
                if attempt < max_retries:
                    print("↻ Riprovo...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("Tutti i tentativi online falliti, passo alla modalità locale...")
                    return process_puml_local(puml_path, svg_path)
            else:
                return process_puml_local(puml_path, svg_path)
    return False

def puml_to_svg():
    input_path, base_name, image_dir, code_dir, output_dir = paths_from_input()
    extra_snippet_dir = os.path.join(code_dir, "extra")

    print("🧩 Generazione immagini da file .puml in corso...")
    puml_root_dirs = [d for d in [code_dir, extra_snippet_dir] if not d.startswith(os.path.join(code_dir, "extra"))]
    svg_count = 0

    for search_dir in puml_root_dirs:
        if os.path.isdir(search_dir):
            for root, _, files in os.walk(search_dir):
                for f in files:
                    if f.lower().endswith(".puml"):
                        puml_path = os.path.join(root, f)
                        rel_subdir = os.path.relpath(root, code_dir)
                        if rel_subdir == ".":
                            svg_dir = image_dir
                        else:
                            svg_dir = os.path.join(image_dir, rel_subdir)

                        os.makedirs(svg_dir, exist_ok=True)
                        svg_name = os.path.splitext(f)[0] + ".svg"
                        svg_path = os.path.join(svg_dir, svg_name)

                        if process_puml(puml_path, svg_path):
                            svg_count += 1

    print(f"\n✅ Generati {svg_count} diagrammi UML totali.\n")
    return input_path, base_name, image_dir, code_dir, output_dir, extra_snippet_dir

def __init__():
    puml_to_svg()