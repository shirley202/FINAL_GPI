// ===============================
//  Enviar pregunta al chatbot
// ===============================
async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();

    if (!text) return;

    addMessage("usuario", text);
    input.value = "";

    // Llamada al backend
    const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
    });

    const data = await res.json();

    // Mostrar respuesta enriquecida
    addMessage("bot", formatearRespuesta(data));
}


// ===============================
//  Formatear la respuesta enriquecida
// ===============================
function formatearRespuesta(r) {
    let html = `
        <div class="respuesta-enriquecida">
            <strong>Respuesta resumida:</strong><br>
            ${r.respuesta}<br><br>

            <strong>Artículo identificado:</strong><br>
            ${r.articulo}<br><br>

            <strong>Fuente:</strong><br>
            ${r.fuente}<br><br>

            <strong>Fragmento original (evidencia):</strong><br>
            <div class="fragmento">
                ${r.fragmento_original}
            </div><br>

            <small>Score: ${r.score.toFixed(3)}</small>
        </div>
    `;

    return html;
}


// ===============================
//  Mostrar mensajes en el chat
// ===============================
function addMessage(remitente, texto) {
    const chat = document.getElementById("chat-window");

    const div = document.createElement("div");
    div.className = "msg " + remitente;
    div.innerHTML = texto;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}
