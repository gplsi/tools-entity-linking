
# tfg_entitylinker/score_utils.py
from tfg_entitylinker.type_filter import TIPOS_OPUESTOS

# Mapeo de tipos NER ↔ tipos P31 válidos
TIPOS_VALIDOS = {
    "PER": {
        "Q5",            # human
        "Q15632617",     # fictional human
        "Q215627"        # person
    },
    "ORG": {
        "Q43229",        # organization
        "Q95074",        # company
        "Q17334923",     # media organization
        "Q7278",         # band
        "Q13406463",     # educational institution
        "Q163740",       # university
        "Q891723",       # political party
        "Q327333",       # nonprofit organization
        "Q79913",        # military unit
        "Q2088357",      # sports team
        "Q1664721"       # government agency
    },
    "LOC": {
        "Q515",          # city
        "Q1549591",      # big city
        "Q6256",         # country
        "Q618123",       # administrative division
        "Q2074737",      # geographic region
        "Q486972",       # human settlement
        "Q82794",        # geographic region (alt)
        "Q5107",         # mountain
        "Q165",          # sea
        "Q8502",         # river
        "Q23397",        # island
        "Q23442",        # peninsula
        "Q355304"        # municipality
    }
}

def score_tipo(tipo_ner, tipos_p31, eliminar_tipos_opuestos=False):
    """
    Devuelve un score normalizado entre -1.0 y 1.0:
    +1.0 si tipo válido
     0.5 si tipo neutro o sin información
    -0.5 si tipo opuesto (y no se elimina)
    """
    if not tipos_p31:
        return 0.5  # sin información, score neutro

    tipos_validos = TIPOS_VALIDOS.get(tipo_ner, set())
    tipos_opuestos = TIPOS_OPUESTOS.get(tipo_ner, set())

    if any(t in tipos_validos for t in tipos_p31):
        return 1.0
    elif any(t in tipos_opuestos for t in tipos_p31):
        if eliminar_tipos_opuestos:
            return None
        else:
            return -0.5
    else:
        return 0.5  # tipo no concluyente


def score_match_exacto(mencion, label_es, label_original, aliases):
    """
    Devuelve 1.0 si la mención coincide exactamente con:
    - el label en español (si existe),
    - el label original,
    - o cualquier alias (en cualquier idioma).
    Devuelve 0.0 en caso contrario.
    """
    m = mencion.strip().lower()

    if label_es and m == label_es.strip().lower():
        return 1.0
    if label_original and m == label_original.strip().lower():
        return 1.0
    if any(m == alias.strip().lower() for alias in aliases or []):
        return 1.0

    return 0.0



def score_calidad(candidato, max_sitelinks):
    """
    Devuelve un score normalizado de calidad basado en número de sitelinks.
    """
    sitelinks = candidato.get("sitelinks", 0)
    return sitelinks / max_sitelinks if max_sitelinks > 0 else 0.0


def calcular_score_total(similitud, tipo_score, match_score, calidad_score=0.0,
                         pesos=(0.45, 0.20, 0.15, 0.20)):
    """
    Combina todos los scores en un único score_total.
    pesos = (similitud, tipo, match, calidad)
    """
    alpha, beta, gamma, delta = pesos
    return (
        alpha * similitud +
        beta * tipo_score +
        gamma * match_score +
        delta * calidad_score
    )
