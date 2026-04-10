from abc import ABC, abstractmethod
from typing import Optional


class IAgentProvider(ABC):

    @abstractmethod
    def ask_agent(
        self,
        agent_id: str,
        agent_alias_id: str,
        session_id: str,
        prompt: str,
        knowledge_base_id: Optional[str] = None,
    ) -> dict:
        ...
