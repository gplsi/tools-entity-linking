import gradio as gr
from tfg_entitylinker import EntityLinker, ConfigEL

class EntityLinkingUI:

    def __init__(self):
        self.config = ConfigEL()
        self.linker = EntityLinker(self.config)

    def predict(self, text, top_n, threshold_score, umbral_absoluto, max_retries):
        try:
            if umbral_absoluto >= threshold_score:
                return "⚠️ El umbral mínimo (umbral absoluto) debe ser menor que el threshold de score."

            self.config.top_n_candidatos = top_n
            self.config.score_threshold = threshold_score
            self.config.umbral_absoluto = umbral_absoluto
            self.config.max_retries = max_retries

            self.linker = EntityLinker(self.config)

            if not text.strip():
                return "Introduce un texto válido."

            entidades = self.linker.link(text)

            if not entidades:
                return "No se encontraron entidades."

            salida = "\n".join(
                f"""🔹 '{e.get('mencion')}' → {e.get('label')} (QID: {e.get('qid')})
                Tipo NER: {e.get('tipo_ner')}, Posición: {e.get('position')}, Longitud: {e.get('length')}
                Descripción: {e.get('descripcion')}
                """
                for e in entidades
            )

            return salida or "No se encontraron entidades con ese umbral de score."

        except Exception as e:
            return f"❌ Error interno: {str(e)}"

    def get_app(self):

        description = """
        <div style='
            position: relative;
            left: 50%;
            transform: translateX(-50%);
            background-color: #004f8b;
            color: white;
            padding: 8px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            width: 100vw;
            box-sizing: border-box;
            margin-bottom: 10px;
        '>
            Entity Linking para Español
        </div>
        """

        article = """
        <div style='
            position: relative;
            left: 50%;
            transform: translateX(-50%);
            width: 100vw;
            background-color: white;
            padding: 15px 0;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-top: 40px;
            border-top: 1px solid #ccc;
            box-sizing: border-box;
        '>
            <img src="/static/logo_cenid.png" alt="CENID" style="height: 60px; max-width: 200px; object-fit: contain;">
            <img src="/static/logo_ua.png" alt="UA" style="height: 60px; max-width: 200px; object-fit: contain;">
            <img src="/static/logo_gplsi.png" alt="GPLSI" style="height: 60px; max-width: 200px; object-fit: contain;">
        </div>

        <script>
            document.title = "EL en Español";
        </script>
        """

        gradio_app = gr.Interface(
            fn=self.predict,
            description=description,
            article=article,
            theme=gr.themes.Base(),
            allow_flagging="never",
            submit_btn=gr.Button("Enviar", variant="primary"),
            clear_btn=gr.Button("Reiniciar", variant="secondary"),
            inputs=[
                gr.Textbox(label="Texto de entrada", lines=7),
                gr.Slider(minimum=1, maximum=20, value=5, step=1, label="Número de candidatos por mención", info="Se recomienda 5 para resultados equilibrados."),
                gr.Slider(minimum=0.1, maximum=1.0, value=0.85, step=0.05, label="Threshold de score", info="Recomendado alrededor de 0.85."),
                gr.Slider(minimum=0.0, maximum=0.9, value=0.3, step=0.05, label="Umbral absoluto de aceptación", info="Recomendado entre 0.3 y 0.4."),
                gr.Slider(minimum=0, maximum=5, value=2, step=1, label="Número máximo de retries por mención", info="Recomendado: 2."),
            ],
            outputs=gr.Textbox(label="Entidades enlazadas", lines=10),
        )

        return gradio_app
