import os
from src.infrastructure.aws.S3Client import S3StorageProvider
from src.infrastructure.aws.KnowledgeBase import BedrockKnowledgeBaseProvider
from src.infrastructure.aws.bedrock_agent import BedrockAgentProvider
from src.application.use_cases.AddKnowledgeToSession import AddKnowledgeToSession
from src.application.use_cases.GetSessionDocuments import GetSessionDocuments
from src.application.use_cases.TerminateSession import TerminateSession
from src.application.use_cases.ask_agent_use_case import AskAgentUseCase


def _region() -> str:
    return os.getenv("REGION", "us-east-2")


def _bucket_name() -> str:
    return os.environ["BUCKET_NAME"]


def _kb_id() -> str:
    return os.environ["KNOWLEDGE_BASE_ID"]


def _data_source_id() -> str:
    return os.environ["DATA_SOURCE_ID"]


# --- Provider factories ---

def get_storage_provider() -> S3StorageProvider:
    return S3StorageProvider(region=_region())


def get_kb_provider() -> BedrockKnowledgeBaseProvider:
    return BedrockKnowledgeBaseProvider(region=_region())


def get_agent_provider() -> BedrockAgentProvider:
    return BedrockAgentProvider(region=_region())


# --- Use case factories (FastAPI Depends-compatible) ---

def get_add_knowledge_use_case() -> AddKnowledgeToSession:
    return AddKnowledgeToSession(
        storage=get_storage_provider(),
        kb_provider=get_kb_provider(),
        bucket_name=_bucket_name(),
        kb_id=_kb_id(),
        data_source_id=_data_source_id(),
    )


def get_session_documents_use_case() -> GetSessionDocuments:
    return GetSessionDocuments(
        storage=get_storage_provider(),
        bucket_name=_bucket_name(),
    )


def get_terminate_session_use_case() -> TerminateSession:
    return TerminateSession(
        storage=get_storage_provider(),
        kb_provider=get_kb_provider(),
        bucket_name=_bucket_name(),
        kb_id=_kb_id(),
        data_source_id=_data_source_id(),
    )


def get_ask_agent_use_case() -> AskAgentUseCase:
    return AskAgentUseCase(
        agent_provider=get_agent_provider(),
        agent_id=os.getenv("AGENT_ID", ""),
        alias_id=os.getenv("ALIAS_ID", "TSTALIASID"),
        knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID", ""),
    )
