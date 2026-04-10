import os
import tempfile
from src.Domain.Interfaces.IStorageProvider import IStorageProvider
from src.Domain.Interfaces.IKnowledgeBaseProvider import IKnowledgeBaseProvider
from src.Domain.ValueObjects.DocumentKey import DocumentKey
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("AddKnowledgeToSession")


class AddKnowledgeToSession:
    def __init__(
        self,
        storage: IStorageProvider,
        kb_provider: IKnowledgeBaseProvider,
        bucket_name: str,
        kb_id: str,
        data_source_id: str,
    ):
        self.storage = storage
        self.kb_provider = kb_provider
        self.bucket_name = bucket_name
        self.kb_id = kb_id
        self.data_source_id = data_source_id

    def execute(self, file_bytes: bytes, file_name: str, session_id: str) -> dict:
        self.storage.ensure_bucket_exists(self.bucket_name)

        s3_key = DocumentKey(session_id=session_id, file_name=file_name).s3_key

        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file_name}") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            self.storage.upload_knowledge_document(
                file_path=tmp_path,
                bucket=self.bucket_name,
                key=s3_key,
            )
            logger.info(f"Documento '{file_name}' enviado para s3://{self.bucket_name}/{s3_key}")
        finally:
            os.remove(tmp_path)

        self.storage.upload_document_metadata(
            bucket=self.bucket_name,
            key=s3_key,
            session_id=session_id,
        )
        logger.info(f"Metadata de sessão '{session_id}' enviado para {s3_key}.metadata.json")

        ingestion_job_id = self.kb_provider.sync_data_source(
            kb_id=self.kb_id,
            data_source_id=self.data_source_id,
        )
        logger.info(f"Sync da Knowledge Base iniciado. Job ID: {ingestion_job_id}")

        return {
            "file_name": file_name,
            "s3_key": s3_key,
            "bucket": self.bucket_name,
            "ingestion_job_id": ingestion_job_id,
        }
