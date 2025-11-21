# ## Naming convention
# # | Endpoint (titolo sezione) | Immagine | Codice |
# # |----------------------------|-----------|--------|
# # | `GET /v1/plants/{id}` | `immagini/get_v1_plants_id.svg` | `snippets/get_v1_plants_id.py` |
# # | `POST /v1/plants/search` | `immagini/post_v1_plants_search.svg` | `snippets/post_v1_plants_search.py` |
# # | `PATCH /v1/plants/{id}` | `immagini/patch_v1_plants_id.svg` | `snippets/patch_v1_plants_id.py` |

def main():
    from src.writeandconvert import write_and_convert
    write_and_convert()

if __name__ == "__main__":
    # python .\documentazione.py plant
    main()
