"""
src/ingest.py — Dalla cartella di documenti all'indice vettoriale.

Pipeline: carica i .md  ->  spezza in chunk  ->  embedda  ->  carica su Qdrant.

Le funzioni di caricamento sono già pronte. In questa versione della challenge devi implementare tu:

- i due chunker (`_chunk_naive` e `_chunk_structure_aware`)
- l'embedding dei chunk
- il caricamento su Qdrant
"""
import re
import uuid
from pathlib import Path

import config
from datapizza.modules.splitters import TextSplitter
from datapizza.type import Chunk, DenseEmbedding
from datapizza.vectorstores.qdrant import QdrantVectorstore
from datapizza.core.vectorstore import VectorConfig, Distance


# ── 1. Caricamento del corpus ────────────────────────────────────────────────
def load_corpus() -> dict[str, str]:
    """Ritorna {nome_file: testo} per tutti i .md in data/corpus/."""
    docs = {}
    for path in sorted(Path(config.CORPUS_DIR).glob("*.md")):
        docs[path.name] = path.read_text(encoding="utf-8")
    if not docs:
        raise FileNotFoundError(f"Nessun .md trovato in {config.CORPUS_DIR}")
    return docs


# ── 2. Chunking ──────────────────────────────────────────────────────────────
def _id_chunk(file: str, testo: str) -> str:
    """Id deterministico dal contenuto: reingerire lo stesso chunk lo sovrascrive."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file}::{testo}"))


def _chunk_naive(file: str, testo: str) -> list[dict]:
    """Chunking 'ingenuo': taglio a caratteri fissi, ignora la struttura."""
    # ── TODO 1 · Chunking naive ──────────────────────────────────────────────
    # Usa TextSplitter(max_char=..., overlap=...) per spezzare `testo` e ritorna una lista
    # di dict nel formato: {"id": ..., "text": ..., "metadata": {"file": file}}
    pezzi = None  # TODO
    
    # ── La seguente riga va tolta quando il TODO è completato:  ────────────
    assert pezzi is not None, "TODO 1 non completato: `pezzi` è ancora None."
    # --------------------------------------------------------------------------
    return pezzi


def _chunk_structure_aware(file: str, testo: str) -> list[dict]:
    """Chunking che segue i titoli markdown e NON spezza i blocchi di codice."""
    # ── TODO 2 · Chunking structure-aware ───────────────────────────────────
    # Obiettivo:
    # 1) non spezzare i blocchi di codice fenced ```...```
    # 2) seguire i titoli markdown quando possibile
    # 3) rispettare config.CHUNK_MAX_CHAR accumulando blocchi fino al limite
    #
    # Suggerimento: puoi prima costruire blocchi "atomici" (paragrafi o code
    # fences intere), poi accumularli in chunk più grandi. Se incontri un
    # titolo markdown, puoi salvarlo in metadata come breadcrumb.
    chunks = None  # TODO

    assert chunks is not None, "TODO 2 non completato: `chunks` è ancora None."
    return chunks


def chunk_corpus(docs: dict[str, str]) -> list[dict]:
    chunkers = {
        "naive": _chunk_naive,
        "structure_aware": _chunk_structure_aware,
    }
    if config.CHUNKER not in chunkers:
        raise ValueError(
            f"CHUNKER non valido: {config.CHUNKER!r}. "
            "Valori ammessi: 'naive', 'structure_aware'."
        )
    fn = chunkers[config.CHUNKER]
    chunks = []
    for nome, testo in docs.items():
        chunks.extend(fn(nome, testo))
    return chunks


# ── 3. Costruzione dell'indice ───────────────────────────────────────────────
def build_index(embedder) -> QdrantVectorstore:
    """
    Costruisce e ritorna un Qdrant in-memory con tutto il corpus indicizzato.
    Usa embedder.dim per dimensionare la collection: cambiando modello la
    dimensione si adatta da sola (è il classico inghippo "ho cambiato modello
    e Qdrant esplode" — qui è gestito leggendo embedder.dim).
    """
    docs = load_corpus()
    chunks = chunk_corpus(docs)
    print(f"Corpus: {len(docs)} documenti -> {len(chunks)} chunk "
          f"(chunker={config.CHUNKER}, max_char={config.CHUNK_MAX_CHAR})")

    # ── TODO 3 · Embedda il testo di tutti i chunk ───────────────────────────
    # Suggerimento: embedder.embed_passages(lista_di_testi) -> lista_di_vettori.
    # Recupera i testi con [c["text"] for c in chunks] e assegna a `vettori`.
    vettori = None  # TODO

    assert vettori is not None and len(vettori) == len(chunks), \
        "TODO 3 non completato: `vettori` deve avere un embedding per chunk."

    # Collection nuova, dimensionata sul modello scelto.
    store = QdrantVectorstore(location=":memory:")
    store.create_collection(
        collection_name=config.COLLECTION,
        vector_config=[VectorConfig(name="dense", dimensions=embedder.dim,
                                    distance=Distance.COSINE)],
    )

    # ── TODO 4 · Carica i chunk su Qdrant ────────────────────────────────────
    # Costruisci un oggetto Chunk per ognuno (id, text, embeddings, metadata) e
    # caricali con store.add(lista, collection_name=config.COLLECTION).
    # L'embedding va passato così: embeddings=[DenseEmbedding(name="dense", vector=v)]
    # TODO

    return store
