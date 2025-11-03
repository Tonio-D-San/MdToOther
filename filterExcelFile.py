import pandas as pd

nomeFile = "Lista_Asset_20250912"
estensione = ".xlsx"
nomeFoglio = "Lista_Asset_20250912"
df = pd.read_excel("Lista_Asset_20250912.xlsx")
risultato = df['pillar'] == 'T'
print(risultato)
