from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.GetSessionDocuments import GetSessionDocuments
from src.application.use_cases.TerminateSession import TerminateSession
from src.application.dtos.document_dtos import SessionDocumentsResponse, TerminateSessionResponse
from src.presentation.api.dependencies import get_session_documents_use_case, get_terminate_session_use_case

router = APIRouter(prefix="/session", tags=["Sessions"])


@router.get(
    "/sessions/{session_id}/history",
    response_model=SessionDocumentsResponse,
    summary="Recuperar histórico de mensagens",
)
async def get_history(
    session_id: str,
    use_case: GetSessionDocuments = Depends(get_session_documents_use_case),
):
    """
    Retorna todos os documentos presentes na base de conhecimento para a sessão informada.
    Consulta o bucket S3 pelo prefixo `sessions/{session_id}/` e devolve a lista de
    arquivos com nome e tamanho.
    """
    try:
        result = use_case.execute(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos da sessão: {str(e)}")

    return SessionDocumentsResponse(
        session_id=result["session_id"],
        documents=result["documents"],
        total=len(result["documents"]),
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=TerminateSessionResponse,
    summary="Encerrar e limpar sessão",
)
async def terminate_session(
    session_id: str,
    use_case: TerminateSession = Depends(get_terminate_session_use_case),
):
    """
    Deleta todos os documentos da base de conhecimento associados à sessão e a reinicia.
    Remove objetos do S3 e dispara Ingestion Job na Knowledge Base.
    """
    try:
        result = use_case.execute(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao encerrar sessão: {str(e)}")

    return TerminateSessionResponse(
        session_id=result["session_id"],
        deleted_documents=result["deleted_documents"],
        message=f"Sessão '{session_id}' encerrada. {result['deleted_documents']} documento(s) removido(s) e Knowledge Base sincronizada.",
    )
