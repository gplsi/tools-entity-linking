# Demo: Entity Linking para Español

Esta demo proporciona una interfaz web para probar un sistema de *Entity Linking* en español. El sistema detecta menciones de entidades en texto libre y las enlaza con entradas correspondientes de Wikidata.

---

## 🧪 ¿Cómo funciona?

1. ✍️ Introduce un texto en español.
2. ⚙️ Ajusta los siguientes parámetros:
   - **Número de candidatos**: cuántas entidades candidatas se consideran por mención (recomendado: 5).
   - **Threshold de score**: puntuación mínima para aceptar un enlace (ej. 0.8).
   - **Umbral absoluto**: puntuación bajo la cual una entidad se descarta directamente (ej. 0.3).
   - **Número máximo de retries**: reintentos si no se supera el umbral (ej. 2).

3. 🚀 Pulsa “Enviar” y recibirás por cada mención:
   - Mención detectada
   - Etiqueta (label) y QID de Wikidata
   - Tipo NER
   - Posición y longitud en el texto
   - Descripción asociada

---

## ▶️ Despliegue local

### 1. Construir la imagen Docker

```bash
docker-compose build --no-cache
```

### 2. Ejecutar la demo

```bash
docker-compose up
```

### 3. Acceder

Abre [http://localhost:8000](http://localhost:8000) en tu navegador.

---

## 📦 Requisitos principales

Declarados en `requirements.txt`:

- [`spaCy==3.7.2`](https://spacy.io/)
- [`sentence-transformers==2.2.2`](https://www.sbert.net/)
- `scikit-learn==1.3.2`
- `numpy==1.24.4`
- `requests==2.31.0`
- `fastapi==0.110.1`
- `uvicorn[standard]==0.29.0`
- `gradio==4.19.2`

> ⚠️ El modelo `paraphrase-multilingual-mpnet-base-v2` se descarga automáticamente al construir la imagen.

---

## 🧾 Créditos y licencias

Este proyecto utiliza software de terceros:

- Modelo `es_core_news_lg` de [spaCy](https://spacy.io/) – MIT License  
- Modelo `paraphrase-multilingual-mpnet-base-v2` de [sentence-transformers](https://www.sbert.net/) – Apache 2.0  
- Datos y API de [Wikidata](https://wikidata.org) – CC0 1.0 Universal  
- Interfaz construida con [Gradio](https://gradio.app/) – Apache 2.0  
- Contenedor gestionado con [Docker](https://www.docker.com/)

---

## 📄 Licencia

Consulta el archivo [`LICENSE`](LICENSE) para ver los términos de uso del proyecto.
