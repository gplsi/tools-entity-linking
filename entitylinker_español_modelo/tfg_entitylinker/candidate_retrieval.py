import requests
import time

def safe_get(url, params=None, max_retries=5, backoff_seconds=30):
    """
    Hace una petición GET segura.
    Si recibe 429 o 503, espera y reintenta.
    """
    for intento in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp
            elif resp.status_code in [429, 503]:
                print(f"[RATE LIMIT] {resp.status_code} en {url} - esperando {backoff_seconds}s (intento {intento + 1})")
                time.sleep(backoff_seconds)
            else:
                print(f"[ERROR] {resp.status_code} en {url}")
                break
        except Exception as e:
            print(f"[EXCEPTION] {e} en {url}")
            time.sleep(backoff_seconds)

    raise RuntimeError(f"[FATAL] Fallos repetidos accediendo a {url}")

class CandidateRetriever:
    """
    Recupera candidatos de entidades desde Wikidata a partir de una mención textual.
    
    - Usa la API de búsqueda `wbsearchentities` para obtener candidatos.
    - Consulta `Special:EntityData` para enriquecer los datos de cada entidad (label, descripción, P31, aliases, sitelinks).
    """
    def __init__(self, language="es", top_n=5):
        self.language = language
        self.top_n = top_n
        self.descripcion_cache = {}

    def buscar_candidatos(self, mencion, limit=None):
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "language": self.language,
            "format": "json",
            "limit": limit or self.top_n,
            "search": mencion
        }
        response = safe_get(url, params=params)
        if response.status_code != 200:
            return []

        resultados = []
        search_results = response.json().get("search", [])

        for item in search_results:
            qid = item.get("id", "")
            label_wb = item.get("label", "")  # Este es el label mostrado en la búsqueda

            detalles = self.obtener_detalles_entidad(qid, label_wb)

            resultados.append({
                "id": qid,
                "label_es": detalles.get("label_es", ""),
                "label_original": detalles.get("label_original", ""),
                "label": detalles.get("label", ""),
                "description": detalles.get("description", ""),
                "p31": detalles.get("p31", []),
                "aliases": detalles.get("aliases", []),
                "sitelinks": detalles.get("sitelinks", 0)
            })

        return resultados

    def obtener_detalles_entidad(self, qid, label_wb=None):
        """
        Consulta Special:EntityData para obtener información detallada de una entidad.
        Incluye: descripción, lista de P31, aliases multilingües y sitelinks.
        """
        if qid in self.descripcion_cache:
            return self.descripcion_cache[qid]

        url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        response = safe_get(url)
        if response.status_code != 200:
            self.descripcion_cache[qid] = {
                "label_es": "",
                "label_original": "",
                "label": "",
                "description": "",
                "p31": [],
                "aliases": [],
                "sitelinks": 0
            }
            return self.descripcion_cache[qid]

        data = response.json()
        entity = data.get("entities", {}).get(qid, {})

        # --- Labels ---
        labels = entity.get("labels", {})
        label_es = labels.get("es", {}).get("value", "")
        label_en = labels.get("en", {}).get("value", "")
        label_any = next((v.get("value", "") for v in labels.values()), "")

        # Aliases multilingües
        aliases_raw = entity.get("aliases", {})
        all_aliases = []
        for lang_aliases in aliases_raw.values():
            all_aliases.extend(a.get("value", "").lower() for a in lang_aliases)
        alias_list = list(set(all_aliases))  # quitar duplicados

        # --- Resolución de label_original ---
        if label_wb:
            label_original = label_wb
        elif label_en:
            label_original = label_en
        elif label_any:
            label_original = label_any
        elif aliases_raw.get("es"):
            label_original = aliases_raw["es"][0]["value"]
        else:
            label_original = ""

        label_final = label_es or label_original

        # Descripción en español
        descriptions = entity.get("descriptions", {})
        descripcion_es = descriptions.get(self.language, {})
        descripcion_final = descripcion_es.get("value", "")

        # P31
        instancias = entity.get("claims", {}).get("P31", [])
        tipos_p31 = [
            c["mainsnak"]["datavalue"]["value"]["id"]
            for c in instancias
            if "datavalue" in c["mainsnak"]
        ]

        # Sitelinks
        sitelinks = entity.get("sitelinks", {})
        num_sitelinks = len(sitelinks)

        resultado = {
            "label_es": label_es,
            "label_original": label_original,
            "label": label_final,
            "description": descripcion_final,
            "p31": tipos_p31,
            "aliases": alias_list,
            "sitelinks": num_sitelinks
        }

        self.descripcion_cache[qid] = resultado
        return resultado
