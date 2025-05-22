class ConfigEL:
    def __init__(
        self,
        top_n_candidatos=5,
        score_threshold=0.8,
        max_retries=2,
        umbral_absoluto=0.3,
        modo_contexto="ventana",
        mostrar_debug=False,

        ventana_contexto=7,
        pesos_score=(0.45, 0.20, 0.15, 0.20),
        language="es",
        eliminar_tipos_opuestos=True,
        ner_model="es_core_news_lg",

        filtrar_por_tipo=True,
        reusar_entidades_anteriores=True,
        bonus_coref_match=0.05,
        bonus_coref_nomatch=0.2
    ):
        self.top_n_candidatos = top_n_candidatos
        self.score_threshold = score_threshold
        self.max_retries = max_retries
        self.umbral_absoluto = umbral_absoluto
        self.modo_contexto = modo_contexto
        self.mostrar_debug = mostrar_debug

        self.ventana_contexto = ventana_contexto
        self.pesos_score = pesos_score
        self.language = language
        self.eliminar_tipos_opuestos = eliminar_tipos_opuestos
        self.ner_model = ner_model

        self.filtrar_por_tipo = filtrar_por_tipo
        self.reusar_entidades_anteriores = reusar_entidades_anteriores

        self.bonus_coref_match = bonus_coref_match
        self.bonus_coref_nomatch = bonus_coref_nomatch
