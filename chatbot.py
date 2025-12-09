import pickle
import numpy as np
import json
import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# === ARCHIVOS ===
TFIDF_FILE = "index_data/indice_tfidf.pkl"
EMB_FILE = "index_data/embeddings.npy"
META_FILE = "index_data/metadata.json"

# === MODELO DE EMBEDDINGS ===
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedder = SentenceTransformer(EMBED_MODEL)

# === CARGA DE ARCHIVOS ===
with open(TFIDF_FILE, "rb") as f:
    data = pickle.load(f)

documentos = data["documentos"]
vectorizer = data["vectorizer"]
embeddings_tfidf = data["embeddings"]
embeddings_dense = np.load(EMB_FILE)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# ================================================================
# EXTRAER NÚMERO DE ARTÍCULO
# ================================================================
def extraer_articulo(texto):
    match = re.search(r"(Artículo\s*\d+º?)", texto, re.IGNORECASE)
    return match.group(1) if match else "No especificado"


# ================================================================
# DETECCIÓN DE TEMA (boost semántico por tipo de reglamento)
# ================================================================
def detectar_tema(pregunta):
    p = pregunta.lower()

    if "pfg" in p or "proyecto final" in p:
        return "PFG"
    if "matr" in p or "acad" in p:
        return "ACADEMICO"
    if "investig" in p:
        return "INVESTIGACION"
    if "falta" in p or "sancion" in p:
        return "GENERAL"

    return None


def documento_es_tema(nombre_pdf, tema):
    nombre = nombre_pdf.lower()

    if tema == "PFG":
        return "pfg" in nombre or "proyecto" in nombre
    if tema == "ACADEMICO":
        return "academ" in nombre
    if tema == "INVESTIGACION":
        return "investig" in nombre
    if tema == "GENERAL":
        return "general" in nombre

    return False


# ================================================================
# FUNCIÓN PRINCIPAL (similaridad + filtros + re-ranking)
# ================================================================
def buscar_respuesta(pregunta: str, k: int = 3):

    # -----------------------
    # 1. TF-IDF
    # -----------------------
    q_vec = vectorizer.transform([pregunta]).toarray().astype("float32")
    sims_tfidf = cosine_similarity(q_vec, embeddings_tfidf)[0]
    top_tfidf = np.argsort(sims_tfidf)[::-1][:k]

    # -----------------------
    # 2. Embeddings densos
    # -----------------------
    q_emb = embedder.encode([pregunta], convert_to_numpy=True)
    sims_dense = cosine_similarity(q_emb, embeddings_dense)[0]
    top_dense = np.argsort(sims_dense)[::-1][:k]

    # -----------------------
    # 3. Unir candidatos
    # -----------------------
    candidatos = list(set(top_tfidf.tolist() + top_dense.tolist()))

    # -----------------------
    # 4. Ranking base
    # -----------------------
    cand_emb = embeddings_dense[candidatos]
    scores = cosine_similarity(q_emb, cand_emb)[0]

    # -----------------------
    # 5. Filtrado por tema
    # -----------------------
    tema = detectar_tema(pregunta)

    if tema:
        for i, idx_real in enumerate(candidatos):
            pdf = documentos[idx_real]["fuente"]

            if documento_es_tema(pdf, tema):
                scores[i] *= 1.40  # fuerte prioridad
            else:
                scores[i] *= 0.55  # penalización fuerte

    # -----------------------
    # 6. Priorización por estructura normativa
    # -----------------------
    for i, idx_real in enumerate(candidatos):
        texto = documentos[idx_real]["texto"]

        if re.search(r"art[ií]culo\s*\d+", texto, re.IGNORECASE):
            scores[i] *= 1.20
        elif re.search(r"cap[ií]tulo|secci[oó]n|t[ií]tulo", texto, re.IGNORECASE):
            scores[i] *= 1.05
        else:
            scores[i] *= 0.85

    # -----------------------
    # 7. Orden final
    # -----------------------
    orden = np.argsort(scores)[::-1]
    mejor_idx = candidatos[orden[0]]

    doc = documentos[mejor_idx]

    # Limpieza básica del fragmento
    fragmento = re.sub(r"\n{2,}", "\n", doc["texto"]).strip()

    return {
        "articulo": extraer_articulo(fragmento),
        "fuente": doc["fuente"],
        "pagina": doc.get("pagina", "No disponible"),
        "fragmento_original": fragmento,
        "score": float(scores[orden[0]])
    }
