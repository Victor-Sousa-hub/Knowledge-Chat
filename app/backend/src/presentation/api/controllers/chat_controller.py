from fastapi import APIRouter, Depends

from src.application.use_cases.ask_agent_use_case import AskAgentUseCase
from src.application.dtos.chat_dtos import ChatRequest, ChatResponse
from src.presentation.api.dependencies import get_ask_agent_use_case

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse, summary="Conversar com o Agente")
async def chat(
    request: ChatRequest,
    use_case: AskAgentUseCase = Depends(get_ask_agent_use_case),
):
    """
    Envia uma pergunta para o Bedrock Agent.
    O Agente utiliza o session_id para manter a memória de curto prazo
    e consulta a Knowledge Base associada para buscar fatos nos documentos.
    """
    return use_case.execute(request)
