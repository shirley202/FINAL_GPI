Chatbot Normativo FCyT – Versión Técnica 2025

Este proyecto implementa un chatbot normativo avanzado para la Facultad de Ciencias y Tecnologías (FCyT – UNCA), diseñado para responder consultas sobre reglamentos, resoluciones y leyes institucionales a partir de archivos PDF.

El objetivo de esta versión es proporcionar una base sólida y extensible, tanto funcional como académica, que permite a los estudiantes comprender la arquitectura, ejecutar el sistema localmente, mejorar el motor de búsqueda y ampliar funcionalidades durante proyectos finales o hackathones.

🧭 ¿Qué hace este sistema?

El chatbot permite realizar preguntas en lenguaje natural sobre los reglamentos de la FCyT y devuelve:

El artículo o sección relevante

El fragmento original exacto del PDF

La página donde se encuentra

La fuente del documento

Flujo interno:

Carga automáticamente todos los PDFs desde la carpeta /docs/.

Extrae el texto completo página por página.

Realiza chunking estructural inteligente:

Detecta Capítulos, Artículos, Secciones y Títulos.

Crea fragmentos alineados al formato jurídico.

Convierte cada fragmento en dos tipos de vectores:

TF-IDF → relevancia por palabras.

Embeddings MiniLM → comprensión semántica profunda.

Búsqueda híbrida + re-ranking semántico y estructural:

Combina los mejores resultados de TF-IDF y embeddings.

Prioriza artículos y capítulos.

Penaliza texto desestructurado.

Reconoce temas (PFG, Académico, Investigación, General).

Esto garantiza que:

Nunca inventa información

Siempre responde únicamente con texto del PDF

Soporta preguntas semánticas, no solo literales

Funciona completamente offline una vez creado el índice

🧩 Requisitos

✔ Python 3.11 recomendado
✔ Conexión inicial a Internet para instalar dependencias

📥 1. Clonar el repositorio
git clone https://github.com/shirley202/FINAL_GPI.git
cd fcyt-chatbot-normativo

🐍 2. Crear y activar entorno virtual
Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1


Si aparece error:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

📦 3. Instalar dependencias
pip install -r requirements.txt


Incluye:

Flask

Sentence-Transformers

PyTorch

NumPy

Scikit-Learn

NLTK

pypdf

📚 4. Estructura del proyecto

Aquí está la sección que querías agregar correctamente formateada:

chatbot-normativo/
├─ app.py                # Servidor web + API
├─ chatbot.py            # Motor híbrido de búsqueda (TF-IDF + Embeddings + Re-ranking)
├─ procesar_pdfs.py      # Indexador estructural con detección de artículos y páginas
├─ index_data/           # Índices TF-IDF, embeddings densos y metadatos
│   ├─ indice_tfidf.pkl
│   ├─ embeddings.npy
│   └─ metadata.json
├─ docs/                 # PDFs normativos
├─ static/
│   ├─ style.css         # Estilos del chatbot web
│   ├─ admin.css         # Estilos del panel administrativo
│   ├─ script.js         # Lógica del frontend del chatbot
│   └─ admin.js          # Lógica del frontend del panel admin
└─ templates/
    ├─ chatbot.html      # Interfaz del chatbot
    └─ admin.html        # Panel administrativo para gestionar PDFs

🏗 5. Procesar los PDFs (generar índices)

Antes de usar el chatbot:

python procesar_pdfs.py


Esto genera:

Archivo	Función
indice_tfidf.pkl	Vectorizador + matriz TF-IDF
embeddings.npy	Embeddings densos MiniLM
metadata.json	Fragmentos, páginas, títulos y fuente
💬 6. Uso del chatbot en consola
python chatbot.py


Ejemplo:

=== Chatbot Normativo – Respuestas Enriquecidas ===
Pregunta: ¿Qué es la naturaleza del PFG?
→ Devuelve artículo, página y fragmento original.

🌐 7. Interfaz Web + Panel Administrativo

Iniciar servidor:

python app.py


Abrir navegador:

http://127.0.0.1:5000/


Incluye:

Chatbot Visual

Interface estilo mensajería

Diferenciación usuario/bot

Fragmentos legales bien formateados

Panel Administrativo

Permite:

Acción	Descripción
Agregar PDF	Sube documento e indexa todo
Reemplazar PDF	Mantiene el nombre pero actualiza el contenido
Eliminar PDF	Lo quita del corpus
Ver PDF	Abre el documento original
🧪 8. Objetivo académico

El proyecto permite que los estudiantes:

Comprendan Recuperación de Información (IR)

Trabajen con TF-IDF y embeddings semánticos

Implementen chunking jurídico (artículos, capítulos, secciones)

Apliquen técnicas de re-ranking híbrido

Construyan un buscador legal real y extensible

Mejoren el motor para su examen, TFG o hackathon

🛠 9. Problemas frecuentes
Problema	Solución
indice_tfidf.pkl no encontrado	Ejecutar python procesar_pdfs.py
Respuestas incorrectas	PDFs escaneados → requiere OCR
Modelo no carga	Revisar instalación de sentence-transformers
Error en servidor	Verificar estructura de carpetas
📄 Licencia

Proyecto educativo de la FCyT–UNCA.
Puede modificarse libremente para investigaciones, exámenes o hackathones.
