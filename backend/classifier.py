import json
import os
from dotenv import load_dotenv

load_dotenv()

# eu leio minha chave/modelo do .env (sem hardcode)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# eu limito o tamanho do texto pra não gastar à toa
MAX_CHARS = 4000

# eu uso essas pistas pro fallback local quando não tiver OpenAI
PALAVRAS_PROD = [
    "problema", "erro", "ajuda", "suporte", "atraso", "falha",
    "bug", "acesso", "login", "senha", "sistema", "ticket",
    "chamado", "pendente", "verificar", "status", "sap"
]

def _sanitizar(texto: str) -> str:
    # eu aparo e corto no limite
    texto = (texto or "").strip()
    if len(texto) > MAX_CHARS:
        texto = texto[:MAX_CHARS]
    return texto

def _fallback_local(texto: str):
    """
    se a OpenAI falhar (ou não houver chave), eu uso regras simples e sigo o jogo
    retorno: (categoria, resposta, origem="local")
    """
    t = (texto or "").lower()
    if any(p in t for p in PALAVRAS_PROD):
        return ("Produtivo", "Obrigado por sua mensagem. Nossa equipe irá analisar sua solicitação em breve.", "local")
    else:
        return ("Improdutivo", "Agradecemos o contato! Estamos sempre à disposição.", "local")

def _normalizar_categoria(cat: str) -> str:
    # eu normalizo qualquer variação pra Produtivo/Improdutivo
    if not cat:
        return "Produtivo"
    c = cat.strip().lower()
    return "Produtivo" if c.startswith("prod") else "Improdutivo"

def classificar_email(texto: str):
    """
    eu tento classificar com OpenAI (JSON certinho). se der ruim, caio no fallback local.
    retorno: (categoria, resposta, origem["openai"|"local"])
    """
    texto = _sanitizar(texto)

    # sem chave -> eu nem tento a openai
    if not OPENAI_API_KEY:
        return _fallback_local(texto)

    try:
        # eu importo aqui dentro pra não forçar dependência quando só quiser local
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        # dica: se quiser timeout global, dá pra usar client = client.with_options(timeout=20.0)

        sistema = (
            "Você classifica emails em APENAS duas categorias:\n"
            "- Produtivo: requer ação/resposta (ex.: suporte, status, dúvida sobre sistema)\n"
            "- Improdutivo: sem ação imediata (ex.: felicitações, agradecimentos)\n"
            "Responda em JSON válido com as chaves 'categoria' e 'resposta'."
        )
        prompt = (
            f'Texto do email:\n"""\n{texto}\n"""\n'
            "Classifique e gere uma resposta curta, profissional e gentil (1–2 frases), em pt-BR."
        )

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        # eu assumo que veio JSON em string por causa do response_format
        content = resp.choices[0].message.content
        dados = json.loads(content)

        categoria = _normalizar_categoria(dados.get("categoria", "Produtivo"))
        resposta  = (dados.get("resposta") or "").strip() or (
            "Obrigado por sua mensagem. Nossa equipe irá analisar sua solicitação em breve."
            if categoria == "Produtivo" else
            "Agradecemos o contato! Estamos sempre à disposição."
        )

        # logzinho pra eu ver no terminal (ótimo pro vídeo)
        usage = getattr(resp, "usage", None)
        print("✅ USANDO OPENAI (free tier primeiro). Modelo:", OPENAI_MODEL, "Usage:", usage)

        return (categoria, resposta, "openai")

    except Exception as e:
        # qualquer erro (quota/rede/etc) -> eu registro e volto pro local
        print("❌ Falha na OpenAI, usando fallback local:", repr(e))
        return _fallback_local(texto)
