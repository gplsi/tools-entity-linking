
import spacy

# Cargar modelo para tokenización
nlp_tokens = spacy.blank("es")  # Solo se necesita el tokenizador
nlp_sentencias = spacy.load("es_core_news_lg")

def get_local_context(texto, start_char, ventana=5):
    '''
    Extrae una ventana de ±ventana palabras alrededor de la mención que comienza en start_char.
    
    Args:
        texto (str): Texto completo.
        start_char (int): Índice de inicio de la mención.
        ventana (int): Número de palabras antes y después.
        
    Returns:
        str: Contexto reducido.
    '''
    doc = nlp_tokens(texto)
    token_start_idx = None

    # Encontrar el token donde empieza la mención
    for i, token in enumerate(doc):
        if token.idx <= start_char < token.idx + len(token):
            token_start_idx = i
            break

    if token_start_idx is None:
        return texto  # Fallback

    start = max(0, token_start_idx - ventana)
    end = min(len(doc), token_start_idx + ventana + 1)
    return doc[start:end].text

def extraer_contexto_oracion(texto, start_char):
    """
    Extrae la oración donde aparece la mención, para usarla como contexto.
    """
    doc = nlp_sentencias(texto)
    for sent in doc.sents:
        if sent.start_char <= start_char <= sent.end_char:
            return sent.text
    return texto  # Fallback si no se encuentra
