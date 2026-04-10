from dataclasses import dataclass, field
from src.Domain.ValueObjects.SessionId import SessionId


@dataclass
class Session:
    id: SessionId
    documents: list[str] = field(default_factory=list)
    is_active: bool = True

    @classmethod
    def create(cls, session_id: str) -> "Session":
        return cls(id=SessionId(session_id))

    def add_document(self, file_name: str) -> None:
        if not self.is_active:
            raise ValueError(f"Cannot add document to terminated session '{self.id}'")
        if file_name not in self.documents:
            self.documents.append(file_name)

    def terminate(self) -> None:
        self.is_active = False
        self.documents.clear()

    def document_count(self) -> int:
        return len(self.documents)
