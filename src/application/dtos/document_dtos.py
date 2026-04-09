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

