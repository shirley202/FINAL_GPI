import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pickle
import time


# ===============================
# CARGA DE MODELOS E ÍNDICES
# ===============================
TFIDF_FILE = "index_data/indice_tfidf.pkl"
EMB_FILE = "index_data/embeddings.npy"
META_FILE = "index_data/metadata.json"

# Modelos
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedder = SentenceTransformer(MODEL_NAME)

with open(TFIDF_FILE, "rb") as f:
    data = pickle.load(f)

documentos = data["documentos"]
vectorizer = data["vectorizer"]
embeddings_tfidf = data["embeddings"]

embeddings_dense = np.load(EMB_FILE)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# ===============================
# FUNCIONES DEL BENCHMARK
# ===============================
def precision_at_k(results, gold, k=3):
    return 1.0 if any(gold in r["texto"] for r in results[:k]) else 0.0


def mrr(results, gold):
    for i, r in enumerate(results):
        if gold in r["texto"]:
            return 1.0 / (i + 1)
    return 0.0


# ===============================
# MÉTODOS DE BÚSQUEDA
# (1) TF-IDF
# (2) Embeddings densos
# (3) Híbrido
# ===============================
def search_tfidf(query, k=3):
    q_vec = vectorizer.transform([query]).toarray().astype("float32")
    sims = cosine_similarity(q_vec, embeddings_tfidf)[0]
    idxs = np.argsort(sims)[::-1][:k]

    return [{"texto": documentos[i]["texto"], "score": float(sims[i])} for i in idxs]


def search_dense(query, k=3):
    q_emb = embedder.encode([query], convert_to_numpy=True)
    sims = cosine_similarity(q_emb, embeddings_dense)[0]
    idxs = np.argsort(sims)[::-1][:k]

    return [{"texto": documentos[i]["texto"], "score": float(sims[i])} for i in idxs]


def search_hybrid(query, k=3):
    q_vec = vectorizer.transform([query]).toarray().astype("float32")
    sims_tfidf = cosine_similarity(q_vec, embeddings_tfidf)[0]

    q_emb = embedder.encode([query], convert_to_numpy=True)
    sims_dense = cosine_similarity(q_emb, embeddings_dense)[0]

    combined = 0.5 * sims_tfidf + 0.5 * sims_dense
    idxs = np.argsort(combined)[::-1][:k]

    return [{"texto": documentos[i]["texto"], "score": float(combined[i])} for i in idxs]


# ===============================
# PREGUNTAS DE PRUEBA
# (Personalizar según los PDFs)
# ===============================
tests = [
    {
        "query": "¿Cuál es la función del docente de la materia PFG?",
        "gold": "Artículo 14"
    },
    {
        "query": "¿Quién puede ser tutor del PFG?",
        "gold": "tutor"
    },
    {
        "query": "¿Qué requisitos debo cumplir para matricular el PFG?",
        "gold": "matricular"
    },
    {
        "query": "¿Qué dice el Artículo 12?",
        "gold": "Artículo 12"
    },
    {
        "query": "¿Qué es un PFG?",
        "gold": "Naturaleza del PFG"
    }
]


# ===============================
# EJECUCIÓN DEL BENCHMARK
# ===============================
print("\n=== EVALUACIÓN DE CALIDAD ===\n")

prec_tfidf = []
prec_dense = []
prec_hybrid = []

mrr_tfidf = []
mrr_dense = []
mrr_hybrid = []

for test in tests:
    q = test["query"]
    gold = test["gold"]

    print(f"\n>>> Pregunta: {q}")

    # --- TF-IDF ---
    r_tfidf = search_tfidf(q)
    p_t = precision_at_k(r_tfidf, gold)
    m_t = mrr(r_tfidf, gold)

    # --- Dense ---
    r_dense = search_dense(q)
    p_d = precision_at_k(r_dense, gold)
    m_d = mrr(r_dense, gold)

    # --- Hybrid ---
    r_hybrid = search_hybrid(q)
    p_h = precision_at_k(r_hybrid, gold)
    m_h = mrr(r_hybrid, gold)

    prec_tfidf.append(p_t)
    prec_dense.append(p_d)
    prec_hybrid.append(p_h)

    mrr_tfidf.append(m_t)
    mrr_dense.append(m_d)
    mrr_hybrid.append(m_h)

    print(f"TF-IDF → Prec@3={p_t:.2f} | MRR={m_t:.2f}")
    print(f"Dense → Prec@3={p_d:.2f} | MRR={m_d:.2f}")
    print(f"Hybrid → Prec@3={p_h:.2f} | MRR={m_h:.2f}")


print("\n==============================")
print("RESULTADOS FINALES")
print("==============================")

print(f"\nTF-IDF PROMEDIO → Prec@3={np.mean(prec_tfidf):.2f} | MRR={np.mean(mrr_tfidf):.2f}")
print(f"Dense PROMEDIO → Prec@3={np.mean(prec_dense):.2f} | MRR={np.mean(mrr_dense):.2f}")
print(f"Hybrid PROMEDIO → Prec@3={np.mean(prec_hybrid):.2f} | MRR={np.mean(mrr_hybrid):.2f}")

print("\n✔ Benchmark finalizado correctamente.\n")
# Guardar resultados para las gráficas
results = {
    "prec_tfidf": prec_tfidf,
    "prec_dense": prec_dense,
    "prec_hybrid": prec_hybrid,
    "mrr_tfidf": mrr_tfidf,
    "mrr_dense": mrr_dense,
    "mrr_hybrid": mrr_hybrid
}

with open("benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("\n✔ Resultados guardados en 'benchmark_results.json'.")
