import os
import requests
from PyPDF2 import PdfReader

API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


def gerar_resposta(texto):
    url = "https://api-inference.huggingface.co/models/gpt2"
    payload = {
        "inputs": f"Email recebido: {texto}\nResposta automática:",
        "parameters": {"max_new_tokens": 50}
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        resultado = response.json()

        texto_gerado = resultado[0]["generated_text"]
        partes = texto_gerado.split("Resposta automática:")
        return partes[1].strip() if len(partes) > 1 else "Resposta gerada com falha"

    except Exception as e:
        print("Erro ao gerar resposta:", e)
        print("Resposta bruta:", response.text)
        return "Erro ao gerar resposta"


def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def preprocess(text: str) -> str:
    return text.lower().strip()
