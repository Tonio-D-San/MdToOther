import re
import unicodedata

def normalize_endpoint(title):
    t = title.lower()
    t = re.sub(r"\*\*", "", t)
    t = unicodedata.normalize("NFKD", t)
    t = re.sub(r"\W+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t

