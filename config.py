"""
config.py — L'UNICO posto in cui si toccano i parametri della pipeline.

Regola d'ordine della challenge: nessun numero "magico" sparso nel codice.
Vuoi cambiare chunker, modello o numero di risultati? Si cambia QUI, una riga,
e si rilancia `python scripts/evaluate.py`. Il resto del codice legge da qui.
"""
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "data" / "corpus"
GOLD_PATH  = BASE_DIR / "data" / "gold" / "queries.json"

# ── LEVA 1 · Modello di embedding ────────────────────────────────────────────
# Valori ammessi: "openai" | "minilm-en" | "minilm-it" | "e5-small" | "bge-m3"
#   openai     -> text-embedding-3-small (1536 dim, serve OPENAI_API_KEY)
#   minilm-en  -> all-MiniLM-L6-v2       (384 dim, gratis, locale, SOLO inglese)
#   minilm-it  -> paraphrase-multilingual-MiniLM-L12-v2 (384 dim, gratis, locale)
#   e5-small   -> intfloat/multilingual-e5-small        (384 dim, gratis, locale)
#   bge-m3     -> BAAI/bge-m3                            (1024 dim, gratis, pesante)
# I modelli locali si scaricano alla prima esecuzione (serve connessione una volta).
EMBEDDER = "minilm-en"   # baseline DEBOLE di proposito: modello solo-inglese su corpus ITALIANO.
                         # Prima vittoria da scoprire: passare a un modello che capisce l'italiano
                         # (minilm-it / e5-small / bge-m3).

# ── LEVA 2 · Chunking ────────────────────────────────────────────────────────
CHUNK_MAX_CHAR  = 1500    # baseline DEBOLE: chunk grossi e grezzi (contesto impreciso). Seconda
CHUNK_OVERLAP   = 0       # vittoria: chunk più piccoli + overlap, o chunking strutturato.
CHUNKER = "naive"         # baseline: taglio a caratteri fissi (ignora la struttura).
# Per un chunking che RISPETTA la struttura non basta cambiare questa stringa: è il
# lavoro di DoclingParser + RecursiveSplitter (come nel demo). Si fa riscrivendo
# build_index in src/ingest.py — è una delle strade per alzare hit@1 (vedi README).

# ── LEVA 3 · Retrieval ───────────────────────────────────────────────────────
TOP_K = 3                 # quanti chunk recuperare per ogni query

# Nome della collection Qdrant (in-memory). Non serve cambiarlo.
COLLECTION = "capstone_docs"
