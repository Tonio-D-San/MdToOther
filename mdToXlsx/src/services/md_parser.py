import re
import pandas as pd

def md_table_to_df(md_lines):
    cleaned = [
        line.strip()
        for line in md_lines
        if re.match(r'^\|.*\|$', line.strip())
    ]
    if len(cleaned) < 2:
        return pd.DataFrame()

    headers = [h.strip() for h in cleaned[0].split('|')[1:-1]]
    rows = [
        [c.strip() for c in line.split('|')[1:-1]]
        for line in cleaned[1:]
    ]

    return pd.DataFrame(rows, columns=headers)

def parse_markdown_tables(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tables = []
    current = []
    inside = False

    for line in lines:
        if re.match(r'^\|', line):
            current.append(line)
            inside = True
        elif inside:
            tables.append(current)
            current = []
            inside = False

    if current:
        tables.append(current)

    return [md_table_to_df(tbl) for tbl in tables if not md_table_to_df(tbl).empty]

