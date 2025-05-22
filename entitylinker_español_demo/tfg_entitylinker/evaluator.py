import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep


def safe_get(url, max_retries=5, backoff_seconds=30):
    """
    Hace una petición GET segura.
    Si recibe 429 (rate limit) o 503 (timeout), espera y reintenta.
    """
    for intento in range(max_retries):
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp
        elif resp.status_code in [429, 503]:
            print(f"[RATE LIMIT] Esperando {backoff_seconds}s por error {resp.status_code} en {url}")
            sleep(backoff_seconds)
        else:
            print(f"[ERROR] {resp.status_code} al acceder a {url}")
            break
    raise RuntimeError(f"[FATAL] Fallos repetidos accediendo a {url} (último status: {resp.status_code})")


def obtener_texto_de_url(url: str) -> str:
    """
    Descarga el contenido de la URL de WikiNews y devuelve el texto plano del artículo.
    Usa safe_get para manejar errores 429/503.
    """
    try:
        resp = safe_get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        contenido = soup.find("div", class_="mw-parser-output")
        if not contenido:
            return ""

        parrafos = contenido.find_all("p")
        texto = "\n".join(p.get_text().strip() for p in parrafos if p.get_text().strip())
        return texto

    except Exception as e:
        print(f"[ERROR] Al procesar {url}: {e}")
        return ""


class Evaluator:
    def __init__(self, linker, mentions_path="mentions.tsv", docs_path="docs.tsv"):
        self.linker = linker
        self.mentions = pd.read_csv(mentions_path, sep="\t")
        self.docs = pd.read_csv(docs_path, sep="\t")
        self.docid_to_url = dict(zip(self.docs["docid"], self.docs["url"]))

    def evaluate(self, max_docs=None, verbose=True, delay=1):
        docids = self.mentions["docid"].unique()
        if max_docs:
            docids = docids[:max_docs]

        total = 0
        aciertos = 0
        mrr_total = 0
        errores = 0
        errores_doc = 0

        for docid in docids:
            url = self.docid_to_url.get(docid)
            if not url:
                continue

            texto = obtener_texto_de_url(url)
            if not texto.strip():
                errores += 1
                print(f"[ERROR] Documento vacío: {docid}")
                continue

            self.linker.entidades_previas = []  # Reset por documento
            if verbose:
                print(f"\n📄 Procesando documento: {docid}")

            menciones_doc = self.mentions[self.mentions["docid"] == docid]

            aciertos_doc = 0
            total_doc = 0
            errores_doc = 0

            for _, row in menciones_doc.iterrows():
                mention = row["mention"]
                qid_gold = row["qid"]
                pos = row["position"]
                length = row["length"]

                try:
                    resultado = self.linker.link_mention_with_context(
                        mention=mention,
                        full_text=texto,
                        start=pos,
                        length=length
                    )
                except Exception as e:
                    print(f"[ERROR] Fallo con '{mention}' en {docid}: {e}")
                    errores += 1
                    errores_doc += 1
                    continue

                total += 1
                total_doc += 1
                if resultado:
                    predicho = resultado["qid"]
                    if predicho == qid_gold:
                        aciertos += 1
                        aciertos_doc += 1
                        mrr_total += 1
                    else:
                        mrr_total += 0
                    if verbose:
                        acierto = predicho == qid_gold
                        simbolo = "✅" if acierto else "❌"
                        print(f"{simbolo} {mention} → {predicho} (esperado: {qid_gold})")
                else:
                    if verbose:
                        print(f"❌ {mention} → None (esperado: {qid_gold})")

            if delay:
                sleep(delay)

            # Accuracy por documento y total
            acc_doc = (aciertos_doc / total_doc) * 100 if total_doc > 0 else 0
            acc_total = (aciertos / total) * 100 if total > 0 else 0

            print(f"📄 Doc terminado: {docid} → "
                  f"aciertos: {aciertos_doc}/{total_doc} ({acc_doc:.2f}%) | "
                  f"acumulado: {aciertos}/{total} ({acc_total:.2f}%) | "
                  f"errores este doc: {errores_doc} | errores totales: {errores}")

        accuracy = aciertos / total if total > 0 else 0
        mrr = mrr_total / total if total > 0 else 0

        print("\n==== RESULTADOS ====")
        print(f"Total menciones evaluadas: {total}")
        print(f"Aciertos exactos (top1): {aciertos}")
        print(f"Accuracy@1: {accuracy:.4f}")
        print(f"MRR: {mrr:.4f}")
        print(f"Errores o vacíos: {errores}")

        return {
            "accuracy@1": round(accuracy, 4),
            "MRR": round(mrr, 4),
            "evaluadas": total,
            "errores": errores
        }
