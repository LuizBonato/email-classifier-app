// Atualiza contador de caracteres
const textarea = document.getElementById("email-texto");
const charCount = document.getElementById("char-count");
textarea.addEventListener("input", () => {
  charCount.textContent = `${textarea.value.length} caracteres`;
});

// Toggle upload de arquivo
const toggleUpload = document.getElementById("toggle-upload");
const uploadWrap = document.getElementById("upload-wrap");
toggleUpload.addEventListener("click", () => {
  uploadWrap.classList.toggle("hidden");
});

// Botão classificar texto
document.getElementById("botao-processar").addEventListener("click", async () => {
  const texto = textarea.value.trim();
  if (!texto) {
    showError("Digite um texto para classificar.");
    return;
  }
  resetUI();
  await classificarTexto(texto);
});

// Botão classificar arquivo
document.getElementById("botao-arquivo").addEventListener("click", async () => {
  const fileInput = document.getElementById("arquivo");
  if (!fileInput.files.length) {
    showError("Selecione um arquivo .txt ou .pdf");
    return;
  }
  resetUI();
  await classificarArquivo(fileInput.files[0]);
});

// Copiar resposta
document.getElementById("btn-copiar").addEventListener("click", () => {
  const resposta = document.getElementById("resposta").textContent;
  navigator.clipboard.writeText(resposta).then(() => {
    document.getElementById("copy-ok").classList.remove("hidden");
    setTimeout(() => {
      document.getElementById("copy-ok").classList.add("hidden");
    }, 2000);
  });
});

// -------- Funções principais --------

// Chama a rota /classificar
async function classificarTexto(texto) {
  try {
    const resp = await fetch("/classificar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    });

    const data = await resp.json();
    if (resp.ok) {
      mostrarResultado(data);
    } else {
      showError(data.erro || "Falha ao classificar");
    }
  } catch (err) {
    showError("Erro de conexão com o servidor");
  }
}

// Chama a rota /classificar-arquivo
async function classificarArquivo(file) {
  const formData = new FormData();
  formData.append("arquivo", file);

  try {
    const resp = await fetch("/classificar-arquivo", {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();
    if (resp.ok) {
      mostrarResultado(data);
    } else {
      showError(data.erro || "Falha ao classificar arquivo");
    }
  } catch (err) {
    showError("Erro de conexão com o servidor");
  }
}

// Mostra resultado na UI
function mostrarResultado(data) {
  document.getElementById("categoria").textContent = data.categoria || "—";
  document.getElementById("resposta").textContent = data.resposta || "—";
  document.getElementById("origem").textContent = `(origem: ${data.origem || "—"})`;
}

// Mostra erro
function showError(msg) {
  const el = document.getElementById("msg-erro");
  el.textContent = msg;
  el.classList.remove("hidden");
}

// Limpa UI antes de nova requisição
function resetUI() {
  document.getElementById("msg-erro").classList.add("hidden");
  document.getElementById("categoria").textContent = "—";
  document.getElementById("resposta").textContent = "—";
  document.getElementById("origem").textContent = "(origem: —)";
}
