import os
import re
import json
import pickle
import unicodedata
import numpy as np
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

# ============================
# CONFIGURACIÓN
# ============================
PDF_DIR = "docs"
INDEX_DIR = "index_data"

os.makedirs(INDEX_DIR, exist_ok=True)

TFIDF_FILE = os.path.join(INDEX_DIR, "indice_tfidf.pkl")
EMB_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
META_FILE = os.path.join(INDEX_DIR, "metadata.json")

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedder = SentenceTransformer(EMBED_MODEL)


# ============================
# NORMALIZACIÓN
# ============================
def normalizar(texto: str) -> str:
    """Limpia texto para embeddings."""
    texto = texto.lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9áéíóúñ.,;:() ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ============================
# EXTRAER PÁGINAS COMPLETAS
# ============================
def extraer_paginas(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    paginas = []

    for num, page in enumerate(reader.pages):
        try:
            texto = page.extract_text()
            if texto:
                paginas.append({"pagina": num + 1, "texto": texto})
        except:
            continue

    return paginas


# ============================
# CHUNKING INTELIGENTE
# ============================
PATRON = re.compile(
    r"(cap[íi]tulo\s+[^\n]+|art[íi]culo\s+\d+º?|art\.\s*\d+|secci[oó]n\s+[^\n]+|t[íi]tulo\s+[^\n]+)",
    re.IGNORECASE
)

def dividir_por_articulos(paginas):
    """Divide cada página en chunks estructurados."""
    chunks = []

    for pag in paginas:
        texto = pag["texto"]
        num_pag = pag["pagina"]

        partes = PATRON.split(texto)

        if len(partes) <= 1:
            chunks.append({
                "titulo": "seccion",
                "texto": texto,
                "pagina": num_pag
            })
            continue

        for i in range(1, len(partes), 2):
            titulo = partes[i].strip()
            contenido = partes[i + 1].strip()

            chunk = f"{titulo}\n{contenido}"

            if len(contenido.split()) < 20:
                continue

            chunks.append({
                "titulo": titulo,
                "texto": chunk,
                "pagina": num_pag
            })

    return chunks


# ============================
# RECONSTRUCCIÓN ÍNDICE
# ============================
def rebuild_index():
    documentos = []

    print("Buscando PDFs en:", PDF_DIR)

    for archivo in os.listdir(PDF_DIR):
        if not archivo.lower().endswith(".pdf"):
            continue

        ruta = os.path.join(PDF_DIR, archivo)
        print(f"\nProcesando: {archivo}")

        paginas = extraer_paginas(ruta)
        chunks = dividir_por_articulos(paginas)

        for c in chunks:
            documentos.append({
                "fuente": archivo,
                "titulo": c["titulo"],
                "texto": c["texto"],
                "pagina": c["pagina"],
                "texto_normal": normalizar(c["texto"])
            })

    print(f"\nTotal de fragmentos: {len(documentos)}")

    textos_norm = [d["texto_normal"] for d in documentos]

    # ============================
    # TF-IDF
    # ============================
    print("\nIndexando TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=25000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(textos_norm)
    embeddings_tfidf = X.toarray().astype("float32")

    with open(TFIDF_FILE, "wb") as f:
        pickle.dump({
            "documentos": documentos,
            "vectorizer": vectorizer,
            "embeddings": embeddings_tfidf
        }, f)

    # ============================
    # EMBEDDINGS DENSOS
    # ============================
    print("\nGenerando embeddings densos...")
    embeddings_dense = embedder.encode(textos_norm, convert_to_numpy=True)
    np.save(EMB_FILE, embeddings_dense)

    # ============================
    # METADATOS
    # ============================
    print("\nGuardando metadatos...")
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(documentos, f, indent=4, ensure_ascii=False)

    print("\n✔ Índice generado con éxito (TF-IDF + Dense + Estructura + Páginas).")


if __name__ == "__main__":
    rebuild_index()
