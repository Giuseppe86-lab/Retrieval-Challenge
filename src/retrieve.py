"""
src/retrieve.py — Data una domanda, recupera i chunk più pertinenti. ★ BASELINE ★

Gira già. Vincolo per il giudice: ritorna oggetti con `.text` e `.metadata["file"]`.
Puoi riscrivere `retrieve` come vuoi (riscrittura query, hybrid, reranking…) purché
mantenga questo contratto.
"""
import config


def retrieve(store, embedder, query: str, k: int | None = None) -> list:
    """Ritorna i `k` chunk più simili alla query. Se k è None usa config.TOP_K."""
    k = k or config.TOP_K
    q_vec = embedder.embed_query(query)
    return store.search(collection_name=config.COLLECTION,
                        query_vector=q_vec, k=k, vector_name="dense")


# ── Bonus (facoltativo) · retrieval ristretto a un file via filtro sui metadati ──
def retrieve_filtered(store, embedder, query: str, file: str, k: int | None = None):
    """Recupera SOLO dai chunk di un certo file. Sfida bonus: implementa il filtro."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue  # noqa: F401
    k = k or config.TOP_K
    q_vec = embedder.embed_query(query)  # noqa: F841
    raise NotImplementedError(
        "Sfida bonus: costruisci un Filter sul campo metadata 'file' e usalo in "
        "store.get_client().query_points(..., using='dense', query_filter=...)."
    )
