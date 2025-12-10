Chatbot Normativo FCyT – Versión Técnica 2025

Este proyecto implementa un chatbot normativo avanzado para la Facultad de Ciencias y Tecnologías (FCyT – UNCA), diseñado para responder consultas sobre reglamentos, resoluciones y leyes institucionales a partir de archivos PDF.

El objetivo de esta versión es proporcionar una base sólida y extensible, tanto funcional como académica, que permite a los estudiantes comprender la arquitectura, ejecutar el sistema localmente, mejorar el motor de búsqueda y ampliar funcionalidades durante proyectos finales o hackathones.

🧭 ¿Qué hace este sistema?

El chatbot permite realizar preguntas en lenguaje natural sobre los reglamentos de la FCyT y devuelve:

El artículo o sección relevante

El fragmento original exacto del PDF

La página donde se encuentra

La fuente del documento

Para esto, el sistema:

1. Carga automáticamente todos los PDFs desde la carpeta docs/.
2. Extrae el texto completo página por página.
3. Realiza un chunking estructural inteligente:

Identifica automáticamente:

Artículos (“Artículo 5º”)

Capítulos (“CAPÍTULO IV”)

Títulos y secciones

Fragmentos insuficientes → descartados
Esto permite que las respuestas sean precisas y alineadas al formato jurídico.

4. Construye dos representaciones vectoriales para cada fragmento:
   TF-IDF

Mide qué tan relevante es cada palabra dentro de cada fragmento.

Embeddings densos MiniLM

Modelo usado:
paraphrase-multilingual-MiniLM-L12-v2
Permite comprender el significado, no solo las palabras exactas.

5. Motor híbrido + re-ranking

Al recibir una pregunta:

Se calcula similitud TF-IDF.

Se calcula similitud semántica mediante embeddings.

Se combinan candidatos.

Se aplica re-ranking:

Artículos → prioridad alta

Capítulos/Secciones → prioridad media

Texto plano → penalización

Se detecta el tema de la pregunta (PFG, Académico, Investigación, General).

Se priorizan documentos del tipo adecuado.

Esto garantiza que:

nunca inventa información

siempre responde con texto real del PDF

soporta consultas semánticas (“¿qué requisitos hay para presentar el PFG?”)

funciona completamente offline una vez creado el índice

🧩 Requisitos
✔ Python 3.11 recomendado

Descarga:

Windows 64-bit:
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

Página oficial:
https://www.python.org/downloads/release/python-3119/

Importante: marcar “Add Python to PATH”.

✔ Conexión a internet

Sólo necesaria la primera vez para descargar dependencias y el modelo MiniLM.

1. Clonar el repositorio
   git clone https://github.com/shirley202/FINAL_GPI.git
   cd cd fcyt-chatbot-normativo
2. Crear y activar el entorno virtual
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

PyTorch (CPU/GPU)

NumPy

Scikit-Learn

pypdf

NLTK

📚 4. Estructura del proyecto
chatbot-normativo/
├─ app.py # Servidor web + API
├─ chatbot.py # Motor híbrido de búsqueda
├─ procesar_pdfs.py # Indexador estructural con embeddings
├─ index_data/ # Índices TF-IDF + embeddings + metadata
├─ docs/ # PDFs normativos
├─ static/
│ ├─ style.css # Estilos del chatbot
│ ├─ admin.css # Estilos del panel admin
│ ├─ script.js # Chat frontend
│ └─ admin.js # Panel admin frontend
└─ templates/
├─ chatbot.html
└─ admin.html

🏗 5. Procesar los PDFs (generar índices)

Antes de usar el chatbot, ejecutar:

python procesar_pdfs.py

Esto genera:

Archivo Función
indice_tfidf.pkl Vectorizador TF-IDF + matriz TF-IDF
embeddings.npy Embeddings densos MiniLM
metadata.json Fragmentos + páginas + títulos

Cada vez que agregues o reemplaces un PDF, se debe reconstruir el índice.

💬 6. Uso del chatbot en modo consola
python chatbot.py

Ejemplo:

=== Chatbot Normativo – Respuestas Enriquecidas ===
Pregunta: ¿Qué es la naturaleza del PFG?
→ Devuelve artículo, página y fragmento original.

🌐 7. Interfaz Web + Panel Administrativo

Iniciar el servidor:

python app.py

Abrir:

http://127.0.0.1:5000/

Incluye:

Chatbot Web

Estilo tipo mensajería

Roles diferenciados (usuario/bot)

Fragmentos legales formateados

Enlace a documentos

Panel Administrativo

Permite:

Función Descripción
Agregar PDF Sube un nuevo documento e indexa todo
Reemplazar PDF Mantiene nombre → actualiza contenido
Eliminar PDF Quita del corpus e indexa
Ver PDF Abre el archivo original

Todo desde el navegador, sin tocar código.

🧪 8. Objetivo académico

Este proyecto busca que los estudiantes:

Comprendan recuperación de información (IR)

Trabajen con TF-IDF y embeddings semánticos

Usen chunking estructural basado en artículos

Integren búsquedas híbridas con re-ranking

Gestionen un corpus documental real

Modifiquen y extiendan el sistema para prácticas, exámenes o TFG

🛠 9. Problemas frecuentes
Problema Solución
indice_tfidf.pkl no encontrado Ejecutar python procesar_pdfs.py
Respuestas incorrectas PDFs escaneados → OCR necesario
Modelo no carga Verificar instalación de sentence-transformers
Error en servidor Revisar estructura de carpetas
📄 Licencia

Proyecto educativo de la FCyT–UNCA.
Puede modificarse libremente para investigaciones, exámenes o hackathones.
