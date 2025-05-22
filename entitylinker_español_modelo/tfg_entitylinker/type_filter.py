# type_filter.py

# Mapeo de tipos NER ↔ tipos P31 opuestos
TIPOS_OPUESTOS = {
    "PER": {
        # Organizaciones
        "Q43229", "Q95074", "Q17334923", "Q7278", "Q13406463", "Q163740", "Q891723", "Q327333",
        # Lugares
        "Q515", "Q1549591", "Q6256", "Q618123", "Q2074737", "Q486972", "Q82794", "Q5107", "Q165", "Q8502", "Q23397", "Q23442", "Q355304"
    },
    "ORG": {
        # Humanos
        "Q5", "Q15632617", "Q215627"
    },
    "LOC": {
        # Humanos
        "Q5", "Q15632617", "Q215627",
        # Organizaciones
        "Q43229", "Q95074", "Q17334923", "Q7278", "Q13406463", "Q163740", "Q891723", "Q327333"
    }
}

def filtrar_por_tipo(candidatos, tipo_ner):
    """
    Elimina solo los candidatos cuyo P31 coincide con un tipo opuesto al NER.
    Mantiene todos los demás, incluso si no son del tipo esperado.
    """
    tipos_opuestos = TIPOS_OPUESTOS.get(tipo_ner, set())
    filtrados = []

    for cand in candidatos:
        tipos_p31 = set(cand.get("p31", []))
        if not tipos_p31:
            filtrados.append(cand)  # sin información, se mantiene
        elif any(t in tipos_opuestos for t in tipos_p31):
            continue  # tipo opuesto → eliminar
        else:
            filtrados.append(cand)  # no opuesto → se mantiene

    return filtrados