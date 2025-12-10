// =============================================
// CARGAR LISTA DE DOCUMENTOS
// =============================================
async function loadDocs() {  
    const res = await fetch("/admin/list");
    const docs = await res.json();

    const tbody = document.getElementById("docs-body");
    tbody.innerHTML = "";   // ← Aquí faltaba un punto y coma

    docs.forEach(doc => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${doc.nombre}</td>
            <td>${(doc.tamano / 1024).toFixed(1)} KB</td>
            <td>${new Date(doc.fecha_mod * 1000).toLocaleString()}</td>
            <td class="acciones">
                <button class="btn ver" onclick="openPDF('${doc.nombre}')">Ver</button>
                <button class="btn reemplazar" onclick="prepareReplace('${doc.nombre}')">Reemplazar</button>
                <button class="btn eliminar" onclick="deletePDF('${doc.nombre}')">Eliminar</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}


// =============================================
// ABRIR PDF EN EL NAVEGADOR
// =============================================
function openPDF(name) {
    window.open("/docs/" + encodeURIComponent(name), "_blank");
}


// =============================================
// SUBIR DOCUMENTO NUEVO
// =============================================
async function uploadPDF() {
    const fileInput = document.getElementById("upload-file");
    if (!fileInput.files.length) return alert("Selecciona un archivo PDF.");

    const form = new FormData();
    form.append("file", fileInput.files[0]);

    await fetch("/admin/upload", {
        method: "POST",
        body: form
    });

    alert("PDF subido y reindexado");
    fileInput.value = "";
    loadDocs();
}


// =============================================
// ELIMINAR DOCUMENTO
// =============================================
async function deletePDF(name) {
    if (!confirm("¿Eliminar " + name + "?")) return;

    await fetch("/admin/delete/" + name, { method: "DELETE" });

    alert("PDF eliminado");
    loadDocs();
}


// =============================================
// REEMPLAZO DE DOCUMENTO
// =============================================
let fileToReplace = null;

function prepareReplace(name) {
    fileToReplace = name;

    document.getElementById("replace-target").innerText =
        "Documento a reemplazar: " + name;

    document.getElementById("replace-box").style.display = "block";
}

async function confirmReplace() {
    const fileInput = document.getElementById("replace-file");

    if (!fileInput.files.length) {
        alert("Selecciona un archivo PDF para reemplazar.");
        return;
    }

    const form = new FormData();
    form.append("file", fileInput.files[0]);

    await fetch("/admin/replace/" + fileToReplace, {
        method: "POST",
        body: form
    });

    alert("Documento reemplazado y reindexado");

    cancelReplace();
    loadDocs();
}

function cancelReplace() {
    document.getElementById("replace-box").style.display = "none";
    document.getElementById("replace-file").value = "";
    fileToReplace = null;
}


// =============================================
// INICIAR
// =============================================
loadDocs();
