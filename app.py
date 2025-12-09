import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from procesar_pdfs import rebuild_index, PDF_DIR
from chatbot import buscar_respuesta

# Flask configurado para servir archivos en /static
app = Flask(__name__, static_folder="static")
CORS(app)

UPLOAD_FOLDER = PDF_DIR
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================
#   RUTA PRINCIPAL (UI CHATBOT)
# ================================
@app.route("/", methods=["GET"])
def home():
    return app.send_static_file("chatbot.html")


# ================================
#   PANEL ADMINISTRATIVO (UI)
# ================================
@app.route("/admin", methods=["GET"])
def admin_panel():
    return app.send_static_file("admin.html")


# ================================
#   SERVIR PDFs DESDE /docs
# ================================
@app.route("/docs/<path:filename>", methods=["GET"])
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)


# ================================
#   CHATBOT
# ================================
@app.route("/ask", methods=["POST"])
def api_ask():
    data = request.json
    query = data.get("query")
    return jsonify(buscar_respuesta(query, k=3))


# ================================
#   ADMINISTRACIÓN
# ================================
@app.route("/admin/list", methods=["GET"])
def list_docs():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.lower().endswith(".pdf"):
            path = os.path.join(UPLOAD_FOLDER, f)
            files.append({
                "nombre": f,
                "tamano": os.path.getsize(path),
                "fecha_mod": os.path.getmtime(path)
            })
    return jsonify(files)


@app.route("/admin/upload", methods=["POST"])
def upload_pdf():
    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"status": "error", "msg": "Solo se permiten archivos PDF"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    rebuild_index()
    return jsonify({"status": "ok", "msg": "Documento agregado"})


@app.route("/admin/replace/<name>", methods=["POST"])
def replace_pdf(name):
    file = request.files["file"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"status": "error", "msg": "Solo se permiten archivos PDF"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, name)
    file.save(save_path)

    rebuild_index()
    return jsonify({"status": "ok", "msg": "Documento reemplazado"})


@app.route("/admin/delete/<name>", methods=["DELETE"])
def delete_pdf(name):
    path = os.path.join(UPLOAD_FOLDER, name)

    if os.path.exists(path):
        os.remove(path)
        rebuild_index()
        return jsonify({"status": "ok", "msg": "Documento eliminado"})

    return jsonify({"status": "error", "msg": "No existe"}), 404


# ================================
#   INICIAR SERVIDOR
# ================================
if __name__ == "__main__":
    app.run(port=5000, debug=True)
