import boto3
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("KBProvider")

class BedrockKnowledgeBaseProvider:
    def __init__(self, region: str = "us-east-2"):
        # Usamos o client 'bedrock-agent' para gerenciar a KB
        self.client = boto3.client("bedrock-agent", region_name=region)

    def sync_data_source(self, kb_id: str, data_source_id: str):
        """
        Força a KB a ler o S3 e atualizar os vetores (Embeddings).
        """
        try:
            logger.info(f"Iniciando Ingestion Job para KB: {kb_id}")
            response = self.client.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id
            )
            return response["ingestionJob"]["ingestionJobId"]
        except Exception as e:
            logger.error(f"Erro ao sincronizar KB: {str(e)}")
            raise e