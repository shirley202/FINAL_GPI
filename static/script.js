async function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value.trim();

    if (!question) return;

    // Mostrar mensaje del usuario
    appendMessage("user", question);

    // Limpiar input
    input.value = "";

    // Enviar al backend
    const res = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query: question})
    });

    const data = await res.json();

    // === Nuevo formato de respuesta ===
    const respuesta = `
        <strong>Artículo:</strong> ${data.articulo}<br>
        <strong>Fuente:</strong> ${data.fuente}<br>
        <strong>Página:</strong> ${data.pagina}<br><br>

        <strong>Fragmento original:</strong><br>
        ${data.fragmento_original}
    `;

    appendMessage("bot", respuesta);
}

function appendMessage(sender, text) {
    const chatWindow = document.getElementById("chat-window");

    const msg = document.createElement("div");
    msg.className = sender === "user" ? "user-message" : "bot-message";
    msg.innerHTML = text;

    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
