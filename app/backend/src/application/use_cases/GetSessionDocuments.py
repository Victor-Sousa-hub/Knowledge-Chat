from src.Domain.Interfaces.IStorageProvider import IStorageProvider
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("GetSessionDocuments")


class GetSessionDocuments:
    def __init__(self, storage: IStorageProvider, bucket_name: str):
        self.storage = storage
        self.bucket_name = bucket_name

    def execute(self, session_id: str) -> dict:
        documents = self.storage.list_session_documents(
            bucket=self.bucket_name,
            session_id=session_id,
        )
        logger.info(f"Sessão {session_id}: {len(documents)} documento(s) encontrado(s)")
        return {"session_id": session_id, "documents": documents}
