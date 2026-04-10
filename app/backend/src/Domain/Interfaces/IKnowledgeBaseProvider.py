from abc import ABC, abstractmethod


class IKnowledgeBaseProvider(ABC):

    @abstractmethod
    def sync_data_source(self, kb_id: str, data_source_id: str) -> str:
        ...
