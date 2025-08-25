// eu deixo a base da API fixa no local (troco quando fizer deploy)
window.API_BASE = window.API_BASE || "http://127.0.0.1:5000";
console.log("[frontend] API_BASE =", window.API_BASE);

document.addEventListener("DOMContentLoaded", () => {
  // pego os elementos que eu uso
  const btn = document.getElementById("botao-processar");
  const textarea = document.getElementById("email-texto");
  const outCat = document.getElementById("categoria");
  const outResp = document.getElementById("resposta");
  const outOrigem = document.getElementById("origem");
  const count = document.getElementById("char-count");

  // upload (se tiver no HTML)
  const uploadLink = document.getElementById("upload-link");
  const fileInput  = document.getElementById("arquivo");

  // helpers de UI
  function setLoading(on) {
    btn.disabled = on;
    btn.textContent = on ? "Classificando..." : "Classificar";
  }
  function setResultado(dados) {
    outCat.textContent   = dados?.categoria || "—";
    outResp.textContent  = dados?.resposta  || "—";
    outOrigem.textContent = `(origem: ${dados?.origem || "—"})`;

    // badge color (só um charme)
    outCat.classList.remove("produtivo", "improdutivo");
    if ((dados?.categoria || "").toLowerCase().startsWith("prod")) outCat.classList.add("produtivo");
    if ((dados?.categoria || "").toLowerCase().startsWith("improd")) outCat.classList.add("improdutivo");
  }
  function showError(msg) {
    alert(msg || "Erro ao processar. Tenta de novo.");
  }

  // contador de caracteres — eu atualizo em tempo real
  function updateCount() {
    count.textContent = `${(textarea.value || "").length} caracteres`;
  }
  textarea.addEventListener("input", updateCount);
  updateCount(); // força atualizar ao carregar

  // clique do botão: eu chamo /classificar
  btn.addEventListener("click", async () => {
    const texto = (textarea.value || "").trim();
    if (!texto) return showError("Digite um texto antes de classificar.");

    setLoading(true);
    try {
      const url = `${window.API_BASE}/classificar`;
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
      });
      const dados = await r.json().catch(() => ({}));
      if (!r.ok) return showError(dados?.erro || `Falha (HTTP ${r.status})`);
      setResultado(dados);
    } catch (e) {
      console.error(e);
      showError("Não consegui falar com o backend. Veja o Console/Network (F12).");
    } finally {
      setLoading(false);
    }
  });

  // upload: eu abro o seletor e mando para /classificar-arquivo
  if (uploadLink && fileInput) {
    uploadLink.addEventListener("click", (e) => {
      e.preventDefault();
      fileInput.click();
    });

    fileInput.addEventListener("change", async () => {
      const file = fileInput.files?.[0];
      if (!file) return;

      setLoading(true);
      try {
        const fd = new FormData();
        fd.append("arquivo", file);
        const url = `${window.API_BASE}/classificar-arquivo`;
        const r = await fetch(url, { method: "POST", body: fd });
        const dados = await r.json().catch(() => ({}));
        if (!r.ok) return showError(dados?.erro || `Falha (HTTP ${r.status})`);
        setResultado(dados);
      } catch (e) {
        console.error(e);
        showError("Não consegui enviar o arquivo para o backend.");
      } finally {
        setLoading(false);
        fileInput.value = ""; // eu limpo o input
      }
    });
  }
});
