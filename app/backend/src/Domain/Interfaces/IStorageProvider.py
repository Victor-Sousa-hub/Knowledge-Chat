from abc import ABC, abstractmethod


class IStorageProvider(ABC):

    @abstractmethod
    def ensure_bucket_exists(self, bucket_name: str) -> None:
        ...

    @abstractmethod
    def upload_knowledge_document(self, file_path: str, bucket: str, key: str) -> None:
        ...

    @abstractmethod
    def upload_document_metadata(self, bucket: str, key: str, session_id: str) -> None:
        ...

    @abstractmethod
    def list_session_documents(self, bucket: str, session_id: str) -> list[dict]:
        ...

    @abstractmethod
    def delete_session_documents(self, bucket: str, session_id: str) -> int:
        ...
