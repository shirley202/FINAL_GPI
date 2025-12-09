import os
import re
import unicodedata
import json
import pickle
import numpy as np
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

# ============================
# CONFIGURACIÓN GENERAL
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
# NORMALIZACIÓN AVANZADA
# ============================
def normalizar(texto):
    """Limpieza profunda para mejorar embeddings & TF-IDF."""
    texto = texto.replace("\n", " ").replace("\r", " ")
    texto = texto.lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9áéíóúñ.,;:() ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ============================
# EXTRAER TEXTO DE PDF
# ============================
def extraer_texto(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    texto = ""
    for p in reader.pages:
        try:
            extraido = p.extract_text()
            if extraido:
                texto += extraido + "\n"
        except:
            continue
    return texto


# ============================
# DETECTAR ESTRUCTURA NORMATIVA
# ============================
PATRON = re.compile(
    r"(cap[ií]tulo\s+\w+|t[ií]tulo\s+\w+|secci[oó]n\s+\w+|art[íi]culo\s+\d+|art\.\s*\d+)",
    re.IGNORECASE
)

def dividir_por_estructura(texto):
    texto = texto.replace("\r", "").strip()
    partes = re.split(PATRON, texto)

    chunks = []

    # estructura: [basura, "Artículo 1", texto1, "Artículo 2", texto2, ...]
    for i in range(1, len(partes), 2):
        etiqueta = partes[i].strip()
        contenido = partes[i+1].strip() if i+1 < len(partes) else ""

        chunks.append({
            "etiqueta": etiqueta,
            "texto": etiqueta + "\n" + contenido
        })

    return chunks


# ============================
# EXPANSIÓN INTELIGENTE
# (Capítulo/Sección → +contenido asociado)
# ============================
def expandir_chunks(chunks):
    """Une títulos con su contenido real si no son artículos."""
    nuevos = []
    buffer = None

    for ch in chunks:
        etiqueta = ch["etiqueta"].lower()

        es_articulo = etiqueta.startswith("art")

        if not es_articulo:
            # Es un título → iniciar buffer
            if buffer:
                nuevos.append(buffer)
            buffer = ch
        else:
            # Es artículo → si hay buffer, unirlo antes
            if buffer:
                nuevos.append(buffer)
                buffer = None
            nuevos.append(ch)

    if buffer:
        nuevos.append(buffer)

    return nuevos


# ============================
# RECONSTRUCCIÓN COMPLETA
# ============================
def rebuild_index():
    print("======================================")
    print(" RECONSTRUYENDO ÍNDICE HÍBRIDO FCyT")
    print("======================================")

    documentos = []

    for archivo in os.listdir(PDF_DIR):
        if not archivo.lower().endswith(".pdf"):
            continue

        ruta = os.path.join(PDF_DIR, archivo)
        print(f"\n📄 Procesando PDF: {archivo}")

        texto = extraer_texto(ruta)
        chunks = dividir_por_estructura(texto)
        chunks = expandir_chunks(chunks)

        for ch in chunks:
            etiqueta = ch["etiqueta"]

            articulo = etiqueta if etiqueta.lower().startswith("art") else None
            cap = etiqueta if etiqueta.lower().startswith(("cap", "sec", "tít")) else None

            documentos.append({
                "fuente": archivo,
                "articulo": articulo,
                "capitulo": cap,
                "texto": ch["texto"],
                "texto_normal": normalizar(ch["texto"])
            })

    print(f"\n🔍 Total de fragmentos estructurales: {len(documentos)}")

    textos_norm = [d["texto_normal"] for d in documentos]

    # ============================
    # TF-IDF
    # ============================
    print("\n⚙ Generando matriz TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=25000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(textos_norm)
    embeddings_tfidf = X.toarray().astype("float32")

    print("💾 Guardando índice TF-IDF...")
    with open(TFIDF_FILE, "wb") as f:
        pickle.dump({
            "documentos": documentos,
            "vectorizer": vectorizer,
            "embeddings": embeddings_tfidf
        }, f)

    # ============================
    # EMBEDDINGS DENSOS
    # ============================
    print("\n⚙ Generando embeddings densos...")
    embeddings_dense = embedder.encode(textos_norm, convert_to_numpy=True, show_progress_bar=True)
    np.save(EMB_FILE, embeddings_dense)

    # ============================
    # METADATOS
    # ============================
    print("💾 Guardando metadatos...")
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(documentos, f, indent=4, ensure_ascii=False)

    print("\n✔ Índice híbrido generado exitosamente.\n")


if __name__ == "__main__":
    rebuild_index()
