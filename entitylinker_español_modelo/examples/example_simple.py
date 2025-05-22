from tfg_entitylinker import EntityLinker, ConfigEL

def main():
    # Texto de prueba con varias entidades reconocibles
    texto = (
        "Pedro Sánchez visitó la Universidad de Alicante y se reunió con Pedro Pascal."
    )

    # Crear configuración y linker
    config = ConfigEL(
        mostrar_debug=True,
        top_n_candidatos=5,
        max_retries=2,
        score_threshold=0.8
    )

    linker = EntityLinker(config=config)

    # Ejecutar linking
    enlaces = linker.link(texto)

    # Mostrar resultados
    print("\n===== RESULTADOS =====")
    for e in enlaces:
        print(f"Mención: '{e['mencion']}'")
        print(f"  ↪ QID: {e['qid']}")
        print(f"  ↪ Label: {e['label']}")
        print(f"  ↪ Descripción: {e['descripcion']}")
        print(f"  ↪ Tipo NER: {e['tipo_ner']}")
        print(f"  ↪ Score: {e['score']}")
        print(f"  ↪ Posición: {e['position']} (len={e['length']})")
        print()

if __name__ == "__main__":
    main()
