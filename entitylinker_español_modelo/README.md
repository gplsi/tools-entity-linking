# 🔗 Entity Linking en Español (TFG)

Este proyecto implementa una librería Python para realizar *Entity Linking* en textos en español. Permite detectar menciones de entidades y enlazarlas con identificadores únicos de Wikidata, utilizando un sistema modular basado en NER, recuperación de candidatos y desambiguación semántica.

## 🚀 Instalación

Puedes instalar la librería localmente desde el repositorio:

```bash
git clone https://github.com/tuusuario/entity-linking-es.git
cd entity-linking-es
pip install .
```

Asegúrate también de instalar el modelo de spaCy:

```bash
python -m spacy download es_core_news_lg
```

## ✅ Versiones probadas

Este sistema ha sido desarrollado y probado con éxito en el siguiente entorno:

| Componente            | Versión utilizada |
|-----------------------|-------------------|
| Python                | 3.10              |
| spaCy                 | 3.8.5             |
| requests              | 2.32.3            |
| sentence-transformers | 4.1.0             |
| scikit-learn          | 1.6.1             |

> ⚠️ Aunque no se imponen versiones estrictas en `requirements.txt`, se recomienda usar versiones iguales o superiores compatibles con estas.

## 📦 Uso básico

```python
from entity_linking import EntityLinker, ConfigEL

# Crear una configuración personalizada (opcional)
config = ConfigEL(
    top_n_candidatos=5,
    score_threshold=0.75,
    max_retries=1,
    umbral_absoluto=0.3,
    mostrar_debug=True,
    ventana_contexto=5,
    pesos_score=(0.4, 0.3, 0.1, 0.2),
    bonus_coref_match=0.1,
    bonus_coref_nomatch=0.25
)

# Crear el linker con esa configuración
linker = EntityLinker(config=config)

# Analizar un texto
texto = "Pedro Sánchez visitó la Universidad de Alicante y se reunió con Pedro Pascal."
resultado = linker.enlazar_entidades(texto)

# Mostrar resultados
for entidad in resultado:
    print(entidad)
```

## ⚙️ Configuración (`ConfigEL`)

Puedes personalizar el comportamiento del sistema mediante la clase `ConfigEL`. Estos son los principales parámetros configurables:

| Parámetro                | Descripción |
|--------------------------|-------------|
| `top_n_candidatos`       | Número de candidatos devueltos por la búsqueda inicial (por mención). |
| `score_threshold`        | Umbral de puntuación total para aceptar un candidato. |
| `max_retries`            | Número de veces que se vuelve a buscar más candidatos si no se supera el umbral. |
| `umbral_absoluto`        | Puntuación mínima absoluta para considerar un candidato viable. |
| `mostrar_debug`          | Si se activa, muestra información de depuración por consola. |
| `ventana_contexto`       | Número de tokens que se usan para formar el contexto local alrededor de la mención. |
| `pesos_score`            | Tupla con los pesos para calcular la puntuación final: `(sim_contexto, tipo, match_textual, calidad)`. |
| `bonus_coref_match`      | Bonus aplicado si la mención coincide con una entidad ya detectada anteriormente. |
| `bonus_coref_nomatch`    | Bonus aplicado si no hay match exacto, pero hay una mención previa similar. |

> ⚠️ Los siguientes parámetros existen pero están sujetos a configuración avanzada o futura documentación:
> `language`, `ner_model`, `eliminar_tipos_opuestos`, `filtrar_por_tipo`, `reusar_entidades_anteriores`, `modo_contexto`.

---

🔎 Consulta el ejemplo completo en [`examples/example_simple.py`](examples/example_simple.py)

## 📂 Estructura del proyecto

```plaintext
entity_linking/     # Código principal del sistema
examples/           # Ejemplo básico de uso
requirements.txt    # Dependencias del proyecto
setup.py            # Instalador de la librería
README.md           # Este archivo
LICENSE             # Licencia del proyecto (MIT)
```

## 📚 Licencias de terceros

Este proyecto hace uso de los siguientes recursos de terceros:

- [`spaCy`](https://spacy.io) (MIT License)
- [`sentence-transformers`](https://www.sbert.net) (Apache License 2.0)
- [Wikidata API](https://www.wikidata.org) (Creative Commons CC0)

Estas dependencias no se redistribuyen directamente, sino que se usan vía instalación o acceso por API.

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---
