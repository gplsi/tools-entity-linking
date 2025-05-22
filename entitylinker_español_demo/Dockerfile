FROM python:3.8-slim

ARG PIP_REQUIREMENTS=requirements.txt

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

COPY $PIP_REQUIREMENTS /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/$PIP_REQUIREMENTS \
 && rm -rf /tmp/pip-tmp

RUN python -m spacy download es_core_news_lg \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')" \
 && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
