# Retrieval Challenge — costruisci la TUA RAG e falla salire

> Esercizio della Lezione 07. Ci fermiamo al **retrieval**: niente generation (quella è la
> prossima lezione). Durata in aula: ~40-50 minuti.

## Lo scenario

Sei un/una AI engineer. Hai un piccolo corpus di documentazione **in italiano** su due database
vettoriali (Qdrant e Pinecone) e un **giudice automatico** (`scripts/evaluate.py`) che misura quanto
bene recuperi i documenti giusti. Parti da una **baseline che gira già** e il tuo lavoro è uno solo:

> **far salire `hit@1`.**

## Come parti (la baseline gira out-of-the-box)

```bash
# venv del corso (o: pip install -r requirements.txt)
python scripts/evaluate.py
```

Non devi completare nessun TODO per iniziare: la pipeline naive è già funzionante e ti stampa il tuo
**hit@1 di partenza**. Default: `EMBEDDER="minilm-it"` (modello locale, **nessuna chiave**),
`CHUNKER="naive"`, `TOP_K=3`.

## La metrica: `hit@1`

Su `N` domande di cui conosciamo la fonte giusta, in quante il documento corretto è il **primo**
risultato. È la misura severa: dice se il retrieval ha *davvero* capito la domanda.

```
  hit@1 =  9/14  ( 64%)  <- PUNTEGGIO
  hit@2 = 13/14  ( 93%)  · solo spareggio
  hit@3 = 14/14  (100%)  · solo spareggio
```

`hit@2` e `hit@3` contano **solo in caso di pareggio** su `hit@1`.

> Perché così semplice? La teoria della valutazione del retrieval (recall, precision, MRR…) è la
> **prossima lezione**. Qui ci serve solo un numero che *sale* quando le tue scelte migliorano.

## Il gioco: migliora come vuoi

La baseline è naive: taglia i documenti a caratteri fissi, ignorando la struttura. **Puoi battere
quel numero come preferisci** — non c'è una sola strada giusta:

- **Cambia le leve** in `config.py`: `EMBEDDER`, `TOP_K`, `CHUNK_MAX_CHAR`, `CHUNK_OVERLAP`.
- **Rispetta la struttura del documento**: la baseline taglia a caratteri e spezza i fatti. La via
  vista a lezione è sostituire il taglio a stringa con `DoclingParser` + `RecursiveSplitter` (con
  `overlap`) dentro `build_index` — esattamente la pipeline del demo.
- **Riscrivi la pipeline**: `build_index` e `retrieve` sono tuoi. Cambia modello, aggiungi una
  riscrittura della query, un reranking… purché `retrieve` rispetti il contratto qui sotto.

**Unico vincolo** (così il giudice continua a funzionare): `retrieve(...)` deve ritornare oggetti con
`.text` e `.metadata["file"]` (il nome del file di provenienza del chunk).

> ⚠️ Ogni modello produce vettori di dimensione diversa (384, 1024, 1536…). Qdrant deve saperlo
> quando crea la collection: lo starter legge `embedder.dim` e dimensiona l'indice da sé, così
> cambi modello senza rompere nulla.

## Le regole d'ordine (valgono quanto il punteggio)

- **Tutti i parametri stanno in `config.py`** — niente numeri magici sparsi nel codice.
- **Ingestion, retrieval e valutazione vivono in file separati.**
- **I dati stanno in `data/`**, il giudice in `scripts/`.

## La consegna che conta

Non basta il numero. Alla fine racconta (2 righe): **quale leva ha mosso `hit@1` e perché.**
"Ho cambiato X e hit@1 è passato da A a B perché…". È lì che si vede chi ha capito, non chi ha
indovinato.

## Struttura del progetto

```
├── config.py            # TUTTE le leve (embedder, chunker, top_k, chunk size/overlap)
├── data/
│   ├── corpus/          # 8 documenti .md (Qdrant + Pinecone), in italiano
│   └── gold/queries.json# 14 domande con la fonte attesa
├── src/
│   ├── embeddings.py    # factory dei modelli: cambi modello con una stringa
│   ├── ingest.py        # BASELINE: load → chunk → embed → Qdrant  (riscrivibile)
│   └── retrieve.py      # BASELINE: query → search → top_k          (riscrivibile)
└── scripts/
    └── evaluate.py      # il giudice (hit@k). NON si tocca.
```

## Sfide bonus (per chi vola)

- **Retrieval filtrato**: implementa `retrieve_filtered` (filtro sui metadati: cerca solo dentro un file).
- **Caccia all'errore**: trova una domanda che sbagli sempre. Colpa del chunking, dell'embedding o di
  com'è scritta la domanda?
- **La tua domanda**: aggiungi una riga al gold set e verifica che la pipeline la gestisca.
- **Chunker strutturato a mano (oltre il corso)**: scrivi tu un chunker che segue i titoli markdown
  e non spezza i blocchi di codice, poi confrontalo con la via `Docling + RecursiveSplitter`. Serve
  a capire *cosa fa* uno splitter strutturato sotto il cofano.
