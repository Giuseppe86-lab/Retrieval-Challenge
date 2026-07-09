"""
src/ingest.py — Dalla cartella di documenti all'indice vettoriale.

★ BASELINE FUNZIONANTE ★ — gira già così com'è. Lancia `python scripts/evaluate.py`
e leggi il tuo hit@1 di partenza. Da qui il gioco è uno solo: FARLO SALIRE.

Hai libertà totale su COME, dalla leva più semplice alla più creativa:
  • config.py              → EMBEDDER, TOP_K, CHUNK_MAX_CHAR, CHUNK_OVERLAP
  • build_index / retrieve → riscrivili come vuoi. Per rispettare la STRUTTURA (come nel
                             demo) sostituisci il taglio a stringa con DoclingParser +
                             RecursiveSplitter; oppure cambia modello, aggiungi reranking, ecc.

UNICO VINCOLO (così il giudice funziona): `retrieve(...)` deve ritornare oggetti con
`.text` e `.metadata["file"]` = nome del file da cui viene il chunk.
"""
import uuid
from pathlib import Path

import config
from datapizza.modules.splitters import TextSplitter
#from datapizza.type import Chunk, DenseEmbedding
from datapizza.vectorstores.qdrant import QdrantVectorstore
from datapizza.core.vectorstore import VectorConfig, Distance

from datapizza.pipeline import IngestionPipeline
from datapizza.modules.parsers.docling import DoclingParser
from datapizza.modules.splitters import RecursiveSplitter
from datapizza.embedders import ChunkEmbedder


# ── 1. Caricamento del corpus ────────────────────────────────────────────────
def load_corpus() -> dict[str, str]:
    """Ritorna {nome_file: testo} per tutti i .md in data/corpus/."""
    docs = {p.name: p.read_text(encoding="utf-8")
            for p in sorted(Path(config.CORPUS_DIR).glob("*.md"))}
    if not docs:
        raise FileNotFoundError(f"Nessun .md trovato in {config.CORPUS_DIR}")
    return docs


def _id_chunk(file: str, testo: str) -> str:
    """Id deterministico dal contenuto: reingerire lo stesso chunk lo sovrascrive."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file}::{testo}"))


# ── 2. Chunking ──────────────────────────────────────────────────────────────
# BASELINE: chunking naive — taglio a caratteri fissi, ignora la struttura.
def _chunk_naive(file: str, testo: str) -> list[dict]:
    pezzi = TextSplitter(max_char=config.CHUNK_MAX_CHAR,
                         overlap=config.CHUNK_OVERLAP).split(testo)
    return [{"id": _id_chunk(file, c.text), "text": c.text,
             "metadata": {"file": file}} for c in pezzi]


def chunk_corpus(docs: dict[str, str]) -> list[dict]:
    # La baseline ha un solo chunker: 'naive'. Per rispettare la STRUTTURA non si aggiunge
    # un chunker a stringa qui: si riscrive build_index con DoclingParser + RecursiveSplitter
    # (come nel demo). Vedi il docstring di build_index e il README.
    if config.CHUNKER != "naive":
        raise ValueError(
            f"CHUNKER={config.CHUNKER!r}: la baseline conosce solo 'naive'. Per il chunking "
            "strutturato riscrivi build_index con Docling + RecursiveSplitter (vedi README)."
        )
    chunks = []
    for nome, testo in docs.items():
        chunks.extend(_chunk_naive(nome, testo))
    return chunks


# ── 3. Costruzione dell'indice ───────────────────────────────────────────────
def build_index(embedder) -> QdrantVectorstore:
    """
    BASELINE: carica → chunk → embed → Qdrant in-memory. Gira già.
    `embedder.dim` dimensiona la collection da sé: cambi modello senza rompere Qdrant.
    Puoi riscrivere questa funzione come vuoi — es. parsare i file con DoclingParser e
    spezzare con RecursiveSplitter (overlap) per rispettare la struttura, come nel demo.
    L'importante è che retrieve() resti interrogabile e che ogni chunk porti metadata["file"].
    """
    EMB_NAME = "dense"
    docs = load_corpus()
    
    #chunks = chunk_corpus(docs)

    # Embedding di tutti i chunk in un colpo solo.
    #vettori = embedder.embed_passages([c["text"] for c in chunks])

    # Collection nuova, dimensionata sul modello scelto.
    store = QdrantVectorstore(location=":memory:")
    store.create_collection(
        collection_name=config.COLLECTION,
        vector_config=[VectorConfig(name=EMB_NAME, dimensions=embedder.dim,
                                    distance=Distance.COSINE)],
    )

    ingestion = IngestionPipeline(
        modules=[
            DoclingParser(),
            RecursiveSplitter(
                max_char=config.CHUNK_MAX_CHAR,
                overlap=config.CHUNK_OVERLAP
            ),
            ChunkEmbedder(client=embedder, embedding_name=EMB_NAME),
        ],
        vector_store=store,
        collection_name=config.COLLECTION,
    )

    # Ingeriamo file per file per attaccare metadata specifici per sorgente.
    for file_name in docs.keys():
        file_path = str(Path(config.CORPUS_DIR) / file_name)
        ingestion.run(file_path=file_path, metadata={"file": file_name})

    chunks = list(store.dump_collection(config.COLLECTION))
    print(f"Corpus: {len(docs)} documenti -> {len(chunks)} chunk "
          f"(chunker={config.CHUNKER}, max_char={config.CHUNK_MAX_CHAR}, "
          f"overlap={config.CHUNK_OVERLAP})")

    # Carica i chunk (testo + vettore + metadata) su Qdrant.
    #store.add(
    #    [Chunk(id=c["id"], text=c["text"],
    #           embeddings=[DenseEmbedding(name="dense", vector=v)],
    #           metadata=c["metadata"])
    #     for c, v in zip(chunks, vettori)],
    #    collection_name=config.COLLECTION,
    #)
    return store

