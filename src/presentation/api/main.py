import os
import sys
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from src.presentation.api.controllers import chat_controller, document_controller
from src.infrastructure.utils.logger import ColorLogger

load_dotenv()

# Inicializa o Logger conforme o requisito (sem prints)
logger = ColorLogger("API_Boot")

REQUIRED_ENV_KEYS = [
    "AWS_BEARER_TOKEN_BEDROCK",
    "BUCKET_NAME",
    "REGION",
    "AGENT_ID",
    "KNOWLEDGE_BASE_ID",
    "DATA_SOURCE_ID",
]

app = FastAPI(
    title="AI Agent API - Bedrock Edition",
    description="Sistema de Chat com IA integrado a Knowledge Bases da AWS",
    version="1.0.0"
)

# Inclusão das rotas (Controllers)
app.include_router(chat_controller.router)
app.include_router(document_controller.router)

@app.on_event("startup")
async def startup_event():
    missing = [key for key in REQUIRED_ENV_KEYS if not os.getenv(key)]
    if missing:
        logger.error(f"Variáveis de ambiente obrigatórias não definidas: {', '.join(missing)}")
        logger.error("Configure o arquivo .env com base no .env.example antes de iniciar.")
        sys.exit(1)
    logger.info("A API está iniciando... Carregando configurações da AWS.")

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "online", "message": "O Agente está ouvindo."}

if __name__ == "__main__":
    # Rodar o servidor: python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)