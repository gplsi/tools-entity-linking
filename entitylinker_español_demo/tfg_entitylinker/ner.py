import spacy

class NERDetector:
    def __init__(self, model_name="es_core_news_lg"):
        self.nlp = spacy.load(model_name)
    
    def detectar_menciones(self, texto):
        """
        Detecta menciones usando el modelo de spaCy.
        Devuelve lista de tuplas: (texto_mencion, start_char, end_char, label)
        """
        doc = self.nlp(texto)
        return [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
