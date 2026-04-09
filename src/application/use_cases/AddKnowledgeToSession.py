import os
import tempfile
from src.infrastructure.aws.S3Client import S3StorageProvider
from src.infrastructure.aws.KnowledgeBase import BedrockKnowledgeBaseProvider
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("AddKnowledgeToSession")


class AddKnowledgeToSession:
    def __init__(self):
        region = os.getenv("REGION", "us-east-1")
        self.s3_provider = S3StorageProvider(region=region)
        self.kb_provider = BedrockKnowledgeBaseProvider(region=region)
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.kb_id = os.getenv("KNOWLEDGE_BASE_ID")
        self.data_source_id = os.getenv("DATA_SOURCE_ID")

    def execute(self, file_bytes: bytes, file_name: str, session_id: str) -> dict:
        self.s3_provider.ensure_bucket_exists(self.bucket_name)

        s3_key = f"sessions/{session_id}/{file_name}"

        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file_name}") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            self.s3_provider.upload_knowledge_document(
                file_path=tmp_path,
                bucket=self.bucket_name,
                key=s3_key,
            )
            logger.info(f"Documento '{file_name}' enviado para s3://{self.bucket_name}/{s3_key}")
        finally:
            os.remove(tmp_path)

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
