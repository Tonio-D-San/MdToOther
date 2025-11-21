import argparse
import os
from datetime import datetime

from dotenv import load_dotenv

from .services.excel_writer import write_tables_to_excel
from .services.md_parser import parse_markdown_tables

def load_and_convert():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Importa tabelle md in Excel formattato.")
    parser.add_argument("--md", help="Nome file markdown senza estensione")
    args = parser.parse_args()

    md_file = f"{args.md if args.md else os.getenv("MD_FILE")}.md"

    excel_input_base = os.getenv("EXCEL_INPUT_FILE")

    print(f"Leggo: {md_file}")
    tables = parse_markdown_tables(md_file)

    if not tables:
        print("Nessuna tabella trovata.")
        return

    write_tables_to_excel(
        excel_input=f"{excel_input_base}.xlsx",
        excel_output=f"{excel_input_base}_{datetime.today().strftime("%d_%m_%y")}.xlsx",
        sheet_name=os.getenv("SHEET_NAME"),
        start_row=int(os.getenv("START_ROW")),
        tables=parse_markdown_tables(md_file)
    )

    print("Importazione completata con successo.")