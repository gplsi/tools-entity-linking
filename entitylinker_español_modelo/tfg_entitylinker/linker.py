from .ner import NERDetector
from .candidate_retrieval import CandidateRetriever
from .config import ConfigEL
from .type_filter import filtrar_por_tipo
from .semantic_similarity import SentenceEncoder, calcular_similitud_contexto_descripcion
from .score_utils import score_tipo, score_match_exacto, calcular_score_total, score_calidad
from .context_utils import get_local_context, extraer_contexto_oracion
from .text_utils import build_entity_text
import time


class EntityLinker:
    def __init__(self, config=None):
        if config is None:
            config = ConfigEL()
        self.config = config
        self.ner = NERDetector(config.ner_model)
        self.encoder = SentenceEncoder()
        self.retriever = CandidateRetriever(
            language=config.language,
            top_n=config.top_n_candidatos
        )
        self.entidades_previas = []
        self.debug_candidatos = []

    def link(self, texto):
        """
        Pipeline principal del EL
        """
        #Buscar entidades con NER
        menciones = self.ner.detectar_menciones(texto)
        enlaces = []
        self.debug_candidatos = []

        for mencion, start, end, label in menciones:
            mejores_candidatos = {}
            encontrados = {}
            m = mencion.lower()

            #Sacar contexto
            contexto = (
                get_local_context(texto, start, ventana=self.config.ventana_contexto)
                if self.config.modo_contexto == "ventana"
                else extraer_contexto_oracion(texto, start)
            )

            #Loop para los retries
            for intento in range(self.config.max_retries + 1):
                n = self.config.top_n_candidatos * (intento + 1)
                if self.config.mostrar_debug:
                    print(f"🔁 Retry {intento+1}: buscando top {n} candidatos para '{mencion}'")

                #Recupera los candidatos
                candidatos = self.retriever.buscar_candidatos(mencion, limit=n)

                enriquecidos = []
                for c in candidatos:
                    detalles = self.retriever.obtener_detalles_entidad(c["id"])
                    c["p31"] = detalles.get("p31", [])
                    c["aliases"] = detalles.get("aliases", [])
                    c["description"] = detalles.get("description", "")
                    c["sitelinks"] = detalles.get("sitelinks", 0)
                    c["label_es"] = detalles.get("label_es", "")
                    c["label_original"] = detalles.get("label_original", "")
                    c["label"] = c["label_es"] or c["label_original"]
                    enriquecidos.append(c)

                #Elimina los de otros tipos
                if self.config.filtrar_por_tipo:
                    enriquecidos = filtrar_por_tipo(enriquecidos, label)

                for c in enriquecidos:
                    encontrados[c["id"]] = c

                #Saca la popularidad
                max_sitelinks = max((e["sitelinks"] for e in encontrados.values()), default=1)

                for c in enriquecidos:
                    matched_alias = next((a for a in c.get("aliases", []) if a.lower() == m), None)
                    texto_entidad = build_entity_text(
                        label=c.get("label", ""),
                        matched_alias=matched_alias,
                        description=c.get("description", "")
                    )
                    #Saca la similitud contextual
                    similitud = calcular_similitud_contexto_descripcion(contexto, texto_entidad, self.encoder)
                    #Saca la puntuación por tipo
                    tipo_score = score_tipo(label, c["p31"], self.config.eliminar_tipos_opuestos)
                    if tipo_score is None:
                        continue
                    #Saca la puntuación de match
                    match_score = score_match_exacto(mencion, c.get("label_es", ""), c.get("label_original", ""), c.get("aliases", []))
                    #Saca la puntuación de popularidad
                    calidad_score = score_calidad(c, max_sitelinks)
                    #Calcula el score total
                    total = calcular_score_total(similitud, tipo_score, match_score, calidad_score, pesos=self.config.pesos_score)
                    c["score_total"] = total
                    mejores_candidatos[c["id"]] = c

                    if self.config.mostrar_debug:
                        self.debug_candidatos.append({
                            "mencion": mencion,
                            "label": c.get("label", ""),
                            "id": c.get("id", ""),
                            "descripcion": c.get("description", ""),
                            "similitud": similitud,
                            "tipo_score": tipo_score,
                            "match_score": match_score,
                            "calidad_score": calidad_score,
                            "bonus": 0.0,
                            "score_total": total,
                            "origen": "candidato"
                        })

                # Early exit si algún candidato supera el threshold
                if any(c["score_total"] >= self.config.score_threshold for c in mejores_candidatos.values()):
                    break

            # Evaluar entidades previas solo una vez
            if self.config.reusar_entidades_anteriores:
                for prev in self.entidades_previas:
                    alias_match = any(m == a.lower() for a in prev["aliases"])
                    label_match = any(m in prev.get(k, "").lower().split() for k in ["label", "label_es", "label_original"])
                    if label_match or alias_match:
                        texto_entidad = build_entity_text(
                            label=prev.get("label", ""),
                            matched_alias=m if m in prev.get("aliases", []) else None,
                            description=prev.get("description", "")
                        )
                        similitud = calcular_similitud_contexto_descripcion(contexto, texto_entidad, self.encoder)
                        tipo_score = score_tipo(label, prev.get("p31", []), self.config.eliminar_tipos_opuestos)
                        if tipo_score is None:
                            continue
                        match_score = score_match_exacto(mencion, prev.get("label_es", ""), prev.get("label_original", ""), prev.get("aliases", []))
                        calidad_score = score_calidad(prev, max_sitelinks)
                        base_score = calcular_score_total(similitud, tipo_score, match_score, calidad_score, self.config.pesos_score)
                        bonus = self.config.bonus_coref_match if match_score == 1.0 else self.config.bonus_coref_nomatch
                        total = base_score + bonus
                        candidato_prev = prev.copy()
                        candidato_prev["score_total"] = total
                        mejores_candidatos[candidato_prev["id"]] = candidato_prev

                        if self.config.mostrar_debug:
                            self.debug_candidatos.append({
                                "mencion": mencion,
                                "label": prev.get("label", ""),
                                "id": prev.get("id", ""),
                                "descripcion": prev.get("description", ""),
                                "similitud": similitud,
                                "tipo_score": tipo_score,
                                "match_score": match_score,
                                "calidad_score": calidad_score,
                                "bonus": bonus,
                                "score_total": total,
                                "origen": "coreferencia"
                            })

            if mejores_candidatos:
                mejor = max(mejores_candidatos.values(), key=lambda x: x["score_total"])
                if mejor["score_total"] >= self.config.umbral_absoluto:
                    enlaces.append({
                        "mencion": mencion,
                        "qid": mejor.get("id", ""),
                        "label": mejor.get("label", ""),
                        "descripcion": mejor.get("description", ""),
                        "tipo_ner": label,
                        "score": round(mejor["score_total"], 3),
                        "position": start,                     
                        "length": end - start 
                    })
                    self.entidades_previas.append({
                        "id": mejor.get("id", ""),
                        "label": mejor.get("label", ""),
                        "label_es": mejor.get("label_es", ""),
                        "label_original": mejor.get("label_original", ""),
                        "aliases": mejor.get("aliases", []),
                        "p31": mejor.get("p31", []),
                        "description": mejor.get("description", ""),
                        "sitelinks": mejor.get("sitelinks", 0)
                    })

        return enlaces

    def obtener_tipo_mencion(self, mention: str, full_text: str, position: int, length: int) -> str:
        """
        Usa spaCy para extraer la frase donde está la mención (usando el offset),
        y ejecuta NER solo sobre esa oración.
        Devuelve el tipo NER (PER, LOC, ORG...) o None si no se detecta.
        """
        doc = self.ner.nlp(full_text)

        # Encontrar la oración que contiene la posición de la mención
        for sent in doc.sents:
            if sent.start_char <= position < sent.end_char:
                oracion = sent.text
                break
        else:
            return None  # No se encontró ninguna frase conteniendo la mención

        entidades = self.ner.detectar_menciones(oracion)  # [(text, start, end, tipo)]
        mention_lower = mention.lower()

        for texto, _, _, tipo in entidades:
            if texto.lower() == mention_lower:
                return tipo

        return None

    
    def link_mention_with_context(self, mention: str, full_text: str, start: int, length: int) -> dict:
        """
        Enlaza una mención concreta dentro de un documento, detectando su tipo NER,
        utilizando contexto local, candidatos de Wikidata y coreferencia.
        Todo el resto es igual que el pipeline anterior
        """

        mejores_candidatos = {}
        encontrados = {}
        m = mention.lower()
        end = start + length

        # Obtener contexto local (frase o ventana)
        contexto = (
            get_local_context(full_text, start, ventana=self.config.ventana_contexto)
            if self.config.modo_contexto == "ventana"
            else extraer_contexto_oracion(full_text, start)
        )

        # Obtener tipo NER para la mención (ej: PER, ORG, etc.)
        tipo_ner = self.obtener_tipo_mencion(mention, full_text, start, length)

        # Buscar candidatos iterativamente
        for intento in range(self.config.max_retries + 1):
            n = self.config.top_n_candidatos * (intento + 1)
            candidatos = self.retriever.buscar_candidatos(mention, limit=n)
            time.sleep(0.2)

            enriquecidos = []
            for c in candidatos:
                detalles = self.retriever.obtener_detalles_entidad(c["id"])
                c["p31"] = detalles.get("p31", [])
                c["aliases"] = detalles.get("aliases", [])
                c["description"] = detalles.get("description", "")
                c["sitelinks"] = detalles.get("sitelinks", 0)
                c["label_es"] = detalles.get("label_es", "")
                c["label_original"] = detalles.get("label_original", "")
                c["label"] = c["label_es"] or c["label_original"]
                enriquecidos.append(c)

            if self.config.filtrar_por_tipo:
                enriquecidos = filtrar_por_tipo(enriquecidos, tipo_ner)

            for c in enriquecidos:
                encontrados[c["id"]] = c

            max_sitelinks = max((e["sitelinks"] for e in encontrados.values()), default=1)

            for c in enriquecidos:
                matched_alias = next((a for a in c.get("aliases", []) if a.lower() == m), None)
                texto_entidad = build_entity_text(
                    label=c.get("label", ""),
                    matched_alias=matched_alias,
                    description=c.get("description", "")
                )
                similitud = calcular_similitud_contexto_descripcion(contexto, texto_entidad, self.encoder)
                tipo_score = score_tipo(tipo_ner, c["p31"], self.config.eliminar_tipos_opuestos)
                if tipo_score is None:
                    continue
                match_score = score_match_exacto(mention, c.get("label_es", ""), c.get("label_original", ""), c.get("aliases", []))
                calidad_score = score_calidad(c, max_sitelinks)
                total = calcular_score_total(similitud, tipo_score, match_score, calidad_score, pesos=self.config.pesos_score)
                c["score_total"] = total
                mejores_candidatos[c["id"]] = c

            if any(c["score_total"] >= self.config.score_threshold for c in mejores_candidatos.values()):
                break

        # Aplicar coreferencia si está activado
        if self.config.reusar_entidades_anteriores:
            for prev in self.entidades_previas:
                alias_match = any(m == a.lower() for a in prev["aliases"])
                label_match = any(m in prev.get(k, "").lower().split() for k in ["label", "label_es", "label_original"])
                if label_match or alias_match:
                    texto_entidad = build_entity_text(
                        label=prev.get("label", ""),
                        matched_alias=m if m in prev.get("aliases", []) else None,
                        description=prev.get("description", "")
                    )
                    similitud = calcular_similitud_contexto_descripcion(contexto, texto_entidad, self.encoder)
                    tipo_score = score_tipo(tipo_ner, prev.get("p31", []), self.config.eliminar_tipos_opuestos)
                    if tipo_score is None:
                        continue
                    match_score = score_match_exacto(mention, prev.get("label_es", ""), prev.get("label_original", ""), prev.get("aliases", []))
                    calidad_score = score_calidad(prev, max_sitelinks)
                    base_score = calcular_score_total(similitud, tipo_score, match_score, calidad_score, self.config.pesos_score)
                    bonus = self.config.bonus_coref_match if match_score == 1.0 else self.config.bonus_coref_nomatch
                    total = base_score + bonus
                    candidato_prev = prev.copy()
                    candidato_prev["score_total"] = total
                    candidato_prev["coreferencia"] = True
                    mejores_candidatos[candidato_prev["id"]] = candidato_prev

        if not mejores_candidatos:
            return None

        mejor = max(mejores_candidatos.values(), key=lambda x: x["score_total"])

        if mejor["score_total"] < self.config.umbral_absoluto:
            return None

        resultado = {
            "mencion": mention,
            "qid": mejor.get("id", ""),
            "label": mejor.get("label", ""),
            "descripcion": mejor.get("description", ""),
            "tipo_ner": tipo_ner,
            "score": round(mejor["score_total"], 3),
            "position": start,
            "length": length
        }

        # Guardar para coreferencia futura
        self.entidades_previas.append({
            "id": mejor.get("id", ""),
            "label": mejor.get("label", ""),
            "label_es": mejor.get("label_es", ""),
            "label_original": mejor.get("label_original", ""),
            "aliases": mejor.get("aliases", []),
            "p31": mejor.get("p31", []),
            "description": mejor.get("description", ""),
            "sitelinks": mejor.get("sitelinks", 0)
        })

        return resultado
