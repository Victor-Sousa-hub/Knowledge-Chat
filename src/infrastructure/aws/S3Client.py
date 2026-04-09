import boto3
from src.infrastructure.utils.logger import ColorLogger

logger = ColorLogger("S3Storage")

class S3StorageProvider:
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