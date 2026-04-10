from src.Domain.Interfaces.IAgentProvider import IAgentProvider
from src.Domain.Services.ChatManager import ChatManager
from src.infrastructure.utils.bedrock_response_parser import BedrockResponseParser
from src.application.dtos.chat_dtos import ChatRequest, ChatResponse, SourceReference


class AskAgentUseCase:
    def __init__(
        self,
        agent_provider: IAgentProvider,
        agent_id: str,
        alias_id: str,
        knowledge_base_id: str,
    ):
        self.chat_manager = ChatManager(
            agent_provider=agent_provider,
            agent_id=agent_id,
            alias_id=alias_id,
            knowledge_base_id=knowledge_base_id,
        )
        self.parser = BedrockResponseParser()

    def execute(self, request: ChatRequest) -> ChatResponse:
        raw = self.chat_manager.ask(
            session_id=request.session_id,
            question=request.question,
        )

        parsed = self.parser.parse(raw)

        return ChatResponse(
            answer=parsed.answer,
            session_id=request.session_id,
            sources=[
                SourceReference(file=src.file_name, uri=src.uri, pages=sorted(src.pages))
                for src in parsed.sources
            ],
        )
