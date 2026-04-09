from fastapi import APIRouter, UploadFile, File, HTTPException
from src.application.dtos.document_dtos import UploadDocumentResponse
from src.application.use_cases.AddKnowledgeToSession import AddKnowledgeToSession

router = APIRouter(prefix="/sessions/{session_id}/documents", tags=["Knowledge"])


@router.post("/", response_model=UploadDocumentResponse, summary="Upload de documento para a base de conhecimento")
async def add_document(session_id: str, file: UploadFile = File(...)):
    allowed_types = {"application/pdf", "text/plain", "text/markdown"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Use PDF, TXT ou Markdown."
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

    try:
        use_case = AddKnowledgeToSession()
        result = use_case.execute(
            file_bytes=file_bytes,
            file_name=file.filename,
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar documento para o S3: {str(e)}")

    return UploadDocumentResponse(
        file_name=result["file_name"],
        s3_key=result["s3_key"],
        bucket=result["bucket"],
        ingestion_job_id=result["ingestion_job_id"],
        message=f"Documento '{result['file_name']}' enviado e sync da Knowledge Base iniciado.",
    )
