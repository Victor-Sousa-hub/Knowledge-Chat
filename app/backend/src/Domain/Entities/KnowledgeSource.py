from dataclasses import dataclass
from src.Domain.ValueObjects.DocumentKey import DocumentKey


@dataclass
class KnowledgeSource:
    file_name: str
    s3_key: str
    bucket: str
    ingestion_job_id: str
    session_id: str

    @classmethod
    def create(
        cls,
        session_id: str,
        file_name: str,
        bucket: str,
        ingestion_job_id: str,
    ) -> "KnowledgeSource":
        key = DocumentKey(session_id=session_id, file_name=file_name).s3_key
        return cls(
            file_name=file_name,
            s3_key=key,
            bucket=bucket,
            ingestion_job_id=ingestion_job_id,
            session_id=session_id,
        )
