import json
import boto3
from src.Domain.Interfaces.IStorageProvider import IStorageProvider
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("S3Storage")

class S3StorageProvider(IStorageProvider):
    def __init__(self, region: str):
        self.s3 = boto3.client("s3", region_name=region)
        self.region = region

    def ensure_bucket_exists(self, bucket_name: str):
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} já existe.")
        except:
            logger.info(f"Criando bucket {bucket_name} na região {self.region}")
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region}
            )

    def upload_knowledge_document(self, file_path: str, bucket: str, key: str):
        logger.info(f"Fazendo upload de {file_path} para {bucket}/{key}")
        self.s3.upload_file(Filename=file_path, Bucket=bucket, Key=key)

    def upload_document_metadata(self, bucket: str, key: str, session_id: str):
        metadata_key = f"{key}.metadata.json"
        metadata = {"metadataAttributes": {"session_id": session_id}}
        logger.info(f"Fazendo upload de metadata para {bucket}/{metadata_key}")
        self.s3.put_object(
            Bucket=bucket,
            Key=metadata_key,
            Body=json.dumps(metadata),
            ContentType="application/json",
        )

    def list_session_documents(self, bucket: str, session_id: str) -> list[dict]:
        prefix = f"sessions/{session_id}/"
        logger.info(f"Listando objetos em s3://{bucket}/{prefix}")
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        return [
            {"name": obj["Key"].replace(prefix, ""), "size": obj["Size"]}
            for obj in contents
            if not obj["Key"].endswith(".metadata.json")
        ]

    def delete_session_documents(self, bucket: str, session_id: str) -> int:
        prefix = f"sessions/{session_id}/"
        logger.info(f"Deletando objetos em s3://{bucket}/{prefix}")
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        if not contents:
            return 0
        objects = [{"Key": obj["Key"]} for obj in contents]
        self.s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})
        logger.info(f"{len(objects)} objeto(s) deletado(s) da sessão {session_id}")
        return len(objects)