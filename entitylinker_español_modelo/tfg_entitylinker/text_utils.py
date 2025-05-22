
def build_entity_text(label, matched_alias, description):
    '''
    Construye un texto enriquecido para similitud semántica.
    
    Incluye:
    - label siempre
    - alias solo si coincide con la mención (matched_alias)
    - descripción si está disponible

    Args:
        label (str): Nombre principal de la entidad.
        matched_alias (str or None): Alias que coincide con la mención.
        description (str): Descripción de Wikidata.

    Returns:
        str: Texto enriquecido.
    '''
    partes = [label.strip()] if label else []
    if matched_alias:
        partes.append(matched_alias.strip())
    if description:
        partes.append(description.strip())
    return ". ".join(partes)
