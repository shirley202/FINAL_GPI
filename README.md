Chatbot Normativo FCyT – Versión Técnica 2025

Este proyecto implementa un chatbot normativo avanzado para la Facultad de Ciencias y Tecnologías (FCyT – UNCA), diseñado para responder consultas sobre reglamentos, resoluciones y leyes institucionales a partir de archivos PDF.

El objetivo de esta versión es proporcionar una base sólida y extensible, tanto funcional como académica, que permite a los estudiantes comprender la arquitectura, ejecutar el sistema localmente, mejorar el motor de búsqueda y ampliar funcionalidades durante proyectos finales o hackathones.

🧭 ¿Qué hace este sistema?

El chatbot permite realizar preguntas en lenguaje natural sobre los reglamentos de la FCyT y devuelve:

El artículo o sección relevante

El fragmento original exacto del PDF

La página donde se encuentra

La fuente del documento

Flujo interno del sistema

Carga automáticamente todos los PDFs desde la carpeta /docs/.

Extrae el texto completo página por página.

Realiza chunking estructural inteligente, identificando artículos, capítulos y secciones.

Convierte cada fragmento en dos vectores:

TF-IDF

Mide la relevancia estadística de las palabras en cada fragmento.

Embeddings MiniLM

Modelo semántico que entiende el significado del texto.
Modelo utilizado:
paraphrase-multilingual-MiniLM-L12-v2

Aplica un motor híbrido de búsqueda + re-ranking:

Combina resultados TF-IDF + embeddings densos

Prioriza artículos y capítulos

Penaliza texto desestructurado

Detecta el tema de la pregunta (PFG, Académico, Investigación, General)

Garantías del sistema

✔ Nunca inventa información
✔ Siempre responde con texto real del PDF
✔ Funciona completamente offline tras generar el índice
✔ Acepta preguntas semánticas, no solo literales

🧩 Requisitos

✔ Python 3.11 recomendado
✔ Conexión a Internet solo la primera vez para descargar dependencias y el modelo MiniLM.

📥 1. Clonar el repositorio
git clone https://github.com/shirley202/FINAL_GPI.git
cd fcyt-chatbot-normativo

🐍 2. Crear y activar entorno virtual
Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1


Si aparece error:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Linux/macOS
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

🏗 4. Procesar los PDFs (generar índices)

Antes de usar el chatbot, generar los vectores:

python procesar_pdfs.py


Esto crea:

Archivo	Función
indice_tfidf.pkl	Vectorizador + matriz TF-IDF
embeddings.npy	Embeddings MiniLM
metadata.json	Fragmentos, páginas, títulos y documento fuente

Cada vez que agregues, borres o reemplaces un PDF debes volver a ejecutar este comando.

💬 5. Uso del chatbot en consola
python chatbot.py


Ejemplo:

=== Chatbot Normativo – Respuestas Enriquecidas ===
Pregunta: ¿Qué es la naturaleza del PFG?
→ Devuelve artículo, página y fragmento original.

🌐 6. Interfaz Web + Panel Administrativo
Ejecutar servidor:
python app.py


Abrir en navegador:

http://127.0.0.1:5000/

Incluye:
Chatbot Visual

Estilo tipo mensajería

Diferencia visual entre usuario y bot

Formato de fragmentos legales bien presentado

Panel Administrativo

Permite gestionar los PDFs:

Acción	Descripción
Agregar PDF	Sube un documento e indexa todo
Reemplazar PDF	Mantiene el nombre y actualiza contenido
Eliminar PDF	Elimina del corpus
Ver PDF	Abre el documento original

Todo accesible desde el navegador, sin necesidad de tocar código.

🧪 7. Objetivo académico

Este proyecto permite que los estudiantes:

Comprendan Recuperación de Información (IR)

Utilicen TF-IDF y embeddings semánticos

Implementen chunking jurídico basado en artículos

Apliquen técnicas modernas de re-ranking

Construyan un buscador legal funcional y extensible

Lo utilicen como base para exámenes, TFG o hackathones

🛠 8. Problemas frecuentes
Problema	Solución
indice_tfidf.pkl no encontrado	Ejecutar python procesar_pdfs.py
Respuestas incorrectas	PDF escaneado → requiere OCR
Error cargando modelo	Reinstalar sentence-transformers
Servidor falla	Revisar estructura de carpetas
📄 Licencia

Proyecto educativo de la FCyT–UNCA.
Libre uso para investigaciones, exámenes y hackathones.