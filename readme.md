<h1 align="center">📧 Classificador de E-mails com Respostas Automáticas</h1>

<p align="center">
  Uma aplicação web que utiliza <b>Flask + OpenAI</b> para classificar e-mails como <b>Produtivos</b> ou <b>Improdutivos</b> e sugerir respostas automáticas.
</p>

---

## ✨ Visão Geral

O fluxo de e-mails em empresas é enorme e, muitas vezes, mensagens **improdutivas** (ex: saudações, spam interno) acabam tirando o foco de mensagens **realmente importantes**.  

Este projeto foi desenvolvido como um **MVP prático** para demonstrar como a IA pode ajudar equipes a **ganhar tempo**, automatizando:  

1. **Classificação** de e-mails (Produtivo x Improdutivo).  
2. **Sugestão de resposta automática** contextualizada.  
3. **Entrada simples** via texto ou upload de arquivos `.txt`/`.pdf`.  

---

## 🌐 Deploy

🔗 Acesse a aplicação em:  
👉 [**email-classifier-app (Render)**](https://email-classifier-app-0knt.onrender.com)

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask + Gunicorn  
- **IA:** OpenAI GPT (gpt-4.1-mini)  
- **Frontend:** HTML + CSS + JavaScript (templates + static do Flask)  
- **Processamento de arquivos:** PyPDF2  
- **Deploy:** Render  

---

## 📂 Estrutura do Projeto

backend/
├── app.py # Flask (rotas, templates e API)
├── classifier.py # Função de classificação com OpenAI + fallback
├── utils.py # Funções auxiliares
├── static/ # Arquivos estáticos (CSS, JS)
│ ├── styles.css
│ └── scripts.js
└── templates/
└── index.html # Interface do usuário

requirements.txt # Dependências


---

## 🚀 Como Executar Localmente

```bash
# Clonar repositório
git clone https://github.com/LuizBonato/email-classifier-app.git
cd email-classifier-app

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Variáveis de ambiente
export OPENAI_API_KEY="sua_chave_api"
export OPENAI_MODEL="gpt-4.1-mini"

# Rodar aplicação  
python -m backend.app
