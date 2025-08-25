import os, time, uuid
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge, NotFound, MethodNotAllowed
from PyPDF2 import PdfReader
import sys, os
sys.path.append(os.path.dirname(__file__))
from classifier import classificar_email


# agora o Flask já sabe onde estão templates/ e static/
app = Flask(__name__, static_folder="static", template_folder="templates")

# json acentuado sem \uXXXX
app.config["JSON_AS_ASCII"] = False

# limite de upload (MB) pra não derrubar o app
MAX_MB = float(os.getenv("MAX_CONTENT_MB", "2"))
app.config["MAX_CONTENT_LENGTH"] = int(MAX_MB * 1024 * 1024)

# CORS só pro que eu liberar (ou localhost por padrão)
default_origins = [
    "http://127.0.0.1:5500", "http://localhost:5500",
    "http://127.0.0.1:3000", "http://localhost:3000"
]
env_origins = os.getenv("FRONT_ORIGINS", "")
allowlist = [o.strip() for o in env_origins.split(",") if o.strip()] or default_origins
CORS(app, resources={r"/*": {"origins": allowlist}})

# helpers simples
def jerr(status, msg, detalhe=None):
    return jsonify({"erro": msg, "detalhe": detalhe, "request_id": g.get("req_id")}), status

def clean(s: str) -> str:
    return (s or "").replace("\x00", "").strip()

# request id e tempo de resposta (bom pra log)
@app.before_request
def _pre():
    g.req_id = uuid.uuid4().hex
    g.t0 = time.perf_counter()

@app.after_request
def _pos(resp):
    resp.headers["X-Request-ID"] = g.get("req_id", "")
    if hasattr(g, "t0"):
        resp.headers["X-Response-Time-ms"] = str(int((time.perf_counter() - g.t0) * 1000))
    return resp

# ---------------- ROTAS ---------------- #

# rota inicial -> frontend
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/healthz")
def health():
    return jsonify({"ok": True}), 200

@app.post("/classificar")
def classificar():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or not data.get("texto"):
        return jerr(400, "Texto vazio ou JSON inválido")

    texto = clean(data["texto"])
    try:
        categoria, resposta, origem = classificar_email(texto)
        return jsonify({
            "categoria": categoria,
            "resposta": resposta,
            "origem": origem,
            "request_id": g.req_id,
            "elapsed_ms": int((time.perf_counter() - g.t0) * 1000)
        }), 200
    except Exception as e:
        return jerr(500, "Erro ao classificar", repr(e))

@app.post("/classificar-arquivo")
def classificar_arquivo():
    f = request.files.get("arquivo")
    if not f:
        return jerr(400, "Nenhum arquivo recebido")

    nome = (f.filename or "").lower()
    try:
        if nome.endswith(".txt"):
            conteudo = clean(f.read().decode("utf-8", errors="ignore"))
        elif nome.endswith(".pdf"):
            reader = PdfReader(f)
            partes = []
            for p in reader.pages:
                t = clean(p.extract_text() or "")
                if t: partes.append(t)
            conteudo = "\n".join(partes)
        else:
            return jerr(415, "Tipo não suportado", "Use .txt ou .pdf")
    except Exception as e:
        return jerr(400, "Falha ao ler arquivo", repr(e))

    if not conteudo:
        return jerr(400, "Arquivo sem texto extraível")

    try:
        categoria, resposta, origem = classificar_email(conteudo)
        return jsonify({
            "categoria": categoria,
            "resposta": resposta,
            "origem": origem,
            "request_id": g.req_id,
            "elapsed_ms": int((time.perf_counter() - g.t0) * 1000)
        }), 200
    except Exception as e:
        return jerr(500, "Erro ao classificar", repr(e))

# ---------------- HANDLERS DE ERRO ---------------- #

@app.errorhandler(NotFound)
def _404(e): return jerr(404, "Rota não encontrada")

@app.errorhandler(MethodNotAllowed)
def _405(e): return jerr(405, "Método não permitido")

@app.errorhandler(RequestEntityTooLarge)
def _413(e): return jerr(413, "Payload muito grande", f"Limite: {app.config['MAX_CONTENT_LENGTH']} bytes")

@app.errorhandler(Exception)
def _500(e): return jerr(500, "Erro interno", repr(e))

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
