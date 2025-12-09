import pickle
import numpy as np
import json
import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# ============================================================
# CONFIGURACIÓN
# ============================================================
TFIDF_FILE = "index_data/indice_tfidf.pkl"
EMB_FILE = "index_data/embeddings.npy"
META_FILE = "index_data/metadata.json"

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedder = SentenceTransformer(EMBED_MODEL)

# ============================================================
# CARGA DE ARCHIVOS
# ============================================================
with open(TFIDF_FILE, "rb") as f:
    data = pickle.load(f)

documentos = data["documentos"]
vectorizer = data["vectorizer"]
embeddings_tfidf = data["embeddings"]

embeddings_dense = np.load(EMB_FILE)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# ============================================================
# CATEGORÍAS TEMÁTICAS (para re-ranking inteligente)
# ============================================================
PATRONES = {
    "documentos": ["documento", "presentar", "entregar", "requisito", "formulario", "nota"],
    "materias": ["materia", "aprobada", "aprobadas", "semestre", "cursado"],
    "defensa": ["defensa", "pública", "tecnica", "tribunal", "calificación"],
    "anteproyecto": ["anteproyecto", "borrador", "presentación", "proyecto"],
    "plazo": ["prórroga", "plazo", "extensión"],
}

def detectar_categoria(pregunta: str):
    pregunta_l = pregunta.lower()
    for categoria, palabras in PATRONES.items():
        if any(p in pregunta_l for p in palabras):
            return categoria
    return None

# ============================================================
# Detectar artículo si existe
# ============================================================
def extraer_articulo(texto):
    match = re.search(r"(Artículo\s*\d+º?)", texto, re.IGNORECASE)
    return match.group(1) if match else "No especificado"

# ============================================================
# Resumen automático semántico
# ============================================================
def resumir_fragmento(fragmento, pregunta):
    frases = re.split(r"[.;]", fragmento)
    frases = [f.strip() for f in frases if len(f.strip()) > 20]

    if not frases:
        return fragmento[:200] + "..."

    q_emb = embedder.encode([pregunta], convert_to_numpy=True)
    frases_emb = embedder.encode(frases, convert_to_numpy=True)

    sims = cosine_similarity(q_emb, frases_emb)[0]
    idx = np.argmax(sims)

    return frases[idx]

# ============================================================
# BÚSQUEDA HÍBRIDA + RE-RANKING AVANZADO
# ============================================================
def buscar_respuesta(pregunta: str, k: int = 3):

    # === SIMILARIDAD TF-IDF ===
    q_vec = vectorizer.transform([pregunta]).toarray().astype("float32")
    sims_tfidf = cosine_similarity(q_vec, embeddings_tfidf)[0]
    top_tfidf = np.argsort(sims_tfidf)[::-1][:k]

    # === SIMILARIDAD EMBEDDINGS ===
    q_emb = embedder.encode([pregunta], convert_to_numpy=True)
    sims_dense = cosine_similarity(q_emb, embeddings_dense)[0]
    top_dense = np.argsort(sims_dense)[::-1][:k]

    # === UNIR CANDIDATOS ===
    candidatos = list(set(top_tfidf.tolist() + top_dense.tolist()))
    candidatos_emb = embeddings_dense[candidatos]

    scores = cosine_similarity(q_emb, candidatos_emb)[0]
    categoria = detectar_categoria(pregunta)

    # ============================================================
    # RE-RANKING SEMÁNTICO + ESTRUCTURAL + TEMÁTICO
    # ============================================================
    for i, idx_local in enumerate(range(len(candidatos))):
        idx_real = candidatos[idx_local]
        doc = documentos[idx_real]
        texto = doc["texto"].lower()

        # PRIORIDAD A ARTÍCULOS
        if re.search(r"art[ií]culo\s*\d+", texto):
            scores[idx_local] *= 1.20

        # PRIORIDAD A CAPÍTULOS / SECCIONES
        elif re.search(r"cap[ií]tulo|secci[oó]n|t[ií]tulo", texto):
            scores[idx_local] *= 1.05

        # --------------------------------------------
        # BOOST TEMÁTICO (MEJORA PEDIDA EN TU GUÍA)
        # --------------------------------------------
        if categoria and any(k in texto for k in PATRONES.get(categoria, [])):
            scores[idx_local] *= 1.30

    # ============================================================
    # ORDEN FINAL
    # ============================================================
    ordenados = np.argsort(scores)[::-1]
    idx_real = candidatos[ordenados[0]]

    doc = documentos[idx_real]
    texto = doc["texto"]
    fuente = doc["fuente"]

    articulo = extraer_articulo(texto)
    resumen = resumir_fragmento(texto, pregunta)

    # ============================================================
    # RESPUESTA FINAL ENRIQUECIDA
    # ============================================================
    respuesta = {
        "respuesta": resumen,
        "articulo": articulo,
        "fragmento_original": texto,
        "fuente": fuente,
        "score": float(scores[ordenados[0]])
    }

    return respuesta

# ============================================================
# MODO CONSOLA PARA PRUEBAS
# ============================================================
if __name__ == "__main__":
    print("=== Chatbot Normativo – Motor Híbrido Mejorado ===")
    while True:
        q = input("\nPregunta: ").strip()
        if q.lower() in {"salir", "exit"}:
            break

        r = buscar_respuesta(q)
        print("\n--- RESPUESTA ---")
        print("Resumen:", r["respuesta"])
        print("Artículo:", r["articulo"])
        print("Fuente:", r["fuente"])
        print("Score:", round(r["score"], 3))
        print("\nFragmento original:\n", r["fragmento_original"])
