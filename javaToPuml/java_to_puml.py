import javalang
import sys
from pathlib import Path

def parse_java_file(file_path):
    """Legge un file Java e ritorna le classi con attributi e metodi"""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = javalang.parse.parse(source)
    classes = []

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        cls = {
            "name": node.name,
            "attributes": [],
            "methods": []
        }
        # attributi
        for field in node.fields:
            for decl in field.declarators:
                cls["attributes"].append(decl.name)
        # metodi
        for method in node.methods:
            cls["methods"].append(method.name)
        classes.append(cls)
    return classes


def generate_puml(classes, output_file):
    """Genera un file .puml a partire dalle classi parsed"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("@startuml\n")
        for cls in classes:
            f.write(f"class {cls['name']} {{\n")
            for attr in cls['attributes']:
                f.write(f"  {attr}\n")
            for method in cls['methods']:
                f.write(f"  {method}()\n")
            f.write("}\n")
        f.write("@enduml\n")
    print(f"✅ PlantUML generato in {output_file}")


def main(java_files, output_file="diagram.puml"):
    all_classes = []
    for jf in java_files:
        all_classes.extend(parse_java_file(jf))
    generate_puml(all_classes, output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python java_to_puml.py MyClass.java [AltraClasse.java ...]")
        sys.exit(1)
    java_files = sys.argv[1:]
    main(java_files)
