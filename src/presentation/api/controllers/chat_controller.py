from fastapi import APIRouter,Depends, HTTPException
from typing import List

from src.application.use_cases.ask_agent_use_case import AskAgentUseCase
from src.infrastructure.aws.bedrock_agent import BedrockAgentProvider
from src.application.dtos.chat_dtos import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

# Simulação de Injeção de Dependência
def get_ask_use_case():
    provider = BedrockAgentProvider(region="us-east-2")
    return AskAgentUseCase(provider)

@router.post("/", response_model=ChatResponse,summary="Conversar com o Agente")
async def chat(request: ChatRequest, use_case: AskAgentUseCase = Depends(get_ask_use_case)):
    """
    Envia uma pergunta para o Bedrock Agent. 
    O Agente utiliza o session_id para manter a memória de curto prazo 
    e consulta a Knowledge Base associada para buscar fatos nos documentos.
    """
    return use_case.execute(request)

@router.get("/sessions/{session_id}/history", summary="Recuperar histórico de mensagens")
async def get_history(session_id: str):
    """
    Busca no banco de dados (DynamoDB/Postgres) todas as trocas de mensagens 
    anteriores desta sessão para reconstruir a interface do usuário.
    """
    # A lógica aqui será chamar o Use Case: get_history_use_case.execute(session_id)
    pass

@router.delete("/sessions/{session_id}", summary="Encerrar e limpar sessão")
async def terminate_session(session_id: str):
    """
    Finaliza a sessão no Bedrock e limpa os metadados temporários no banco.
    Útil para quando o usuário deseja 'limpar o chat'.
    """
    pass

