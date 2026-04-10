from src.Domain.Interfaces.IAgentProvider import IAgentProvider


class ChatManager:
    """
    Domain service responsible for orchestrating a chat interaction.
    Encapsulates which agent and knowledge base to use — knowledge that
    belongs to the domain, not to infrastructure or application layers.
    """

    def __init__(
        self,
        agent_provider: IAgentProvider,
        agent_id: str,
        alias_id: str,
        knowledge_base_id: str,
    ):
        self._agent_provider = agent_provider
        self._agent_id = agent_id
        self._alias_id = alias_id
        self._knowledge_base_id = knowledge_base_id

    def ask(self, session_id: str, question: str) -> dict:
        return self._agent_provider.ask_agent(
            agent_id=self._agent_id,
            agent_alias_id=self._alias_id,
            session_id=session_id,
            prompt=question,
            knowledge_base_id=self._knowledge_base_id,
        )
