from src.Domain.Interfaces.IStorageProvider import IStorageProvider
from src.Domain.Interfaces.IKnowledgeBaseProvider import IKnowledgeBaseProvider
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("TerminateSession")


class TerminateSession:
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

    def execute(self, session_id: str) -> dict:
        deleted = self.storage.delete_session_documents(
            bucket=self.bucket_name,
            session_id=session_id,
        )
        logger.info(f"Sessão {session_id}: {deleted} documento(s) removido(s) do S3")

        self.kb_provider.sync_data_source(
            kb_id=self.kb_id,
            data_source_id=self.data_source_id,
        )
        logger.info(f"Sync da Knowledge Base iniciado após encerramento da sessão {session_id}")

        return {"session_id": session_id, "deleted_documents": deleted}
