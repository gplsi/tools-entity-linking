from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SentenceEncoder:
    """
    Clase para codificar oraciones en vectores mediante un modelo de Sentence-Transformers.
    Por defecto, usa un modelo multilingüe preentrenado.
    """
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-mpnet-base-v2'):
        self.model = SentenceTransformer(model_name)

    def encode(self, sentences):
        return self.model.encode(sentences, convert_to_numpy=True)

def calcular_similitud_contexto_descripcion(contexto, descripcion, encoder):
    """
    Calcula la similitud entre el contexto y la descripción de una entidad
    usando embeddings y la similitud del coseno.
    Retorna:
    - similitud: valor entre -1 y 1 (normalmente entre 0 y 1)
    """
    embeddings = encoder.encode([contexto, descripcion])
    similitud = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similitud
