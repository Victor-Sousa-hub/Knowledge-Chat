import os
from dotenv import load_dotenv
load_dotenv()

from src.infrastructure.aws.bedrock_agent import BedrockAgentProvider
from src.infrastructure.utils.bedrock_response_parser import BedrockResponseParser
from src.application.dtos.chat_dtos import ChatRequest, ChatResponse, SourceReference

class AskAgentUseCase:
    def __init__(self, agent_provider: BedrockAgentProvider):
        self.agent_provider = agent_provider
        self.parser = BedrockResponseParser()

    def execute(self, request: ChatRequest) -> ChatResponse:
        agent_id = os.getenv("AGENT_ID", "")
        alias_id = os.getenv("ALIAS_ID", "TSTALIASID")
        knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "")

        raw = self.agent_provider.ask_agent(
            agent_id=agent_id,
            agent_alias_id=alias_id,
            session_id=request.session_id,
            prompt=request.question,
            knowledge_base_id=knowledge_base_id
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