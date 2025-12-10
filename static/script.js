async function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value.trim();

    if (!question) return;

    appendMessage("user", question);
    input.value = "";

    const res = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query: question})
    });

    const data = await res.json();

    // Crear tarjeta visual del bot
    const respuesta = `
        <div class="respuesta-card">
            <div class="respuesta-header">
                <strong>${data.articulo}</strong>
            </div>

            <div class="respuesta-meta">
                <p><strong>Fuente:</strong> ${data.fuente}</p>
                <p><strong>Página:</strong> ${data.pagina}</p>
                <p><strong>Score:</strong> ${data.score.toFixed(3)}</p>
            </div>

            <div class="respuesta-fragmento">
                ${data.fragmento_original}
            </div>
        </div>
    `;

    appendMessage("bot", respuesta);
}

function appendMessage(sender, text) {
    const chatWindow = document.getElementById("chat-window");

    const wrapper = document.createElement("div");
    wrapper.className = sender === "user" ? "msg-user" : "msg-bot";

    wrapper.innerHTML = `
        <div class="bubble">
            ${text}
        </div>
    `;

    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
