import aioboto3
import os
from contextlib import asynccontextmanager
from minio import Minio
from app.config.config_app import settings
from dotenv import load_dotenv
load_dotenv()

mc = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False  # Для HTTP (не HTTPS)
)

# Создаем единый bucket для всех файлов
bucket_name = settings.MINIO_BUCKET

found = mc.bucket_exists(bucket_name)
if not found:
    mc.make_bucket(bucket_name)


@asynccontextmanager
async def get_boto_client():
    url = f"http://{os.getenv("MINIO_HOST")}:{os.getenv("MINIO_PORT")}"
    session = aioboto3.Session()
    async with session.client(
        's3',
        endpoint_url=url,  # Для MinIO
        aws_access_key_id=os.getenv("MINIO_USER"),
        aws_secret_access_key=os.getenv("MINIO_PASSWORD"),
        region_name='us-east-1'
    ) as client:
        yield client
