from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Domain.Entities.Sessions import Session


class ISessionRepository(ABC):

    @abstractmethod
    def save(self, session: "Session") -> None:
        ...

    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional["Session"]:
        ...

    @abstractmethod
    def delete(self, session_id: str) -> None:
        ...
