import aioboto3
import os
from minio import Minio

mc = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_USER"),
    secret_key=os.getenv("MINIO_PASSWORD"),
    secure=False  # Для HTTP (не HTTPS)
)

buckets = ["answers", "comments", "tasks"]

for bucket in buckets:
    found = mc.bucket_exists(bucket)
    if not found:
        mc.make_bucket(bucket)





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
