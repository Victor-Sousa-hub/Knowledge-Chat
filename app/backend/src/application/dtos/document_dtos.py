from pydantic import BaseModel
from typing import List, Optional

class DocumentInfo(BaseModel):
    name: str
    pages: int

class UploadDocumentResponse(BaseModel):
    file_name: str
    s3_key: str
    bucket: str
    ingestion_job_id: str
    message: str

class SessionDocument(BaseModel):
    name: str
    size: int

class SessionDocumentsResponse(BaseModel):
    session_id: str
    documents: List[SessionDocument]
    total: int

class TerminateSessionResponse(BaseModel):
    session_id: str
    deleted_documents: int
    message: str

