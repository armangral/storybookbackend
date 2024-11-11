import io
from typing import List, Optional

import aioboto3
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

from app.core.config import settings


class WasabiClient:
    """Encapsulates interactions with Wasabi S3 storage."""

    def __init__(self, endpoint_url: str, access_key: str, secret_key: str) -> None:
        """Initializes the Wasabi client.

        Args:
            endpoint_url (str): The Wasabi endpoint URL.
            access_key (str): The Wasabi access key ID.
            secret_key (str): The Wasabi secret access key.
        """

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    async def list_buckets(self) -> List[dict]:
        """Lists all Wasabi buckets.

        Returns:
            List[dict]: A list of bucket information dictionaries.
        """

        return self.s3_client.list_buckets()["Buckets"]

    async def list_objects(self, bucket_name: str) -> Optional[List[dict]]:
        """Lists objects in a specific bucket.

        Args:
            bucket_name (str): The name of the bucket to list objects from.

        Returns:
            Optional[List[dict]]: A list of object summaries, or None if the bucket is empty.
        """

        paginator = self.s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket_name)

        objects = []
        for page in page_iterator:
            if "Contents" in page:
                objects.extend(page["Contents"])

        return objects or None  # Return None if the bucket is empty


async def get_wasabi_client() -> WasabiClient:
    """Creates and returns a WasabiClient instance, configured from settings."""

    return WasabiClient(
        endpoint_url=settings.WASABI_API_BASE_URL,
        access_key=settings.WASABI_ACCESS_KEY,
        secret_key=settings.WASABI_SECRET_KEY,
    )


async def upload_to_s3(file, bucket, key):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        file_content = await file.read()
        print(f"key is {key}")
        await s3.upload_fileobj(
            Fileobj=io.BytesIO(file_content),
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentDisposition": f"attachment; filename = {file.filename}"},
        )


async def save(file: UploadFile, bucket: str, object_key: str):
    await upload_to_s3(file, bucket, object_key)


async def s3_download_file(file, key_folder):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        s3_response = await s3.get_object(
            Bucket=settings.WASABI_BUCKET_NAME, Key=f"{key_folder}/{file.name_internal}"
        )
        file_content = await s3_response["Body"].read()
    return file_content




async def s3_download_file_with_name(file_name_internal, key_folder):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        try:
            items = []
            s3_response = await s3.get_object(
                Bucket=settings.WASABI_BUCKET_NAME,
                Key=f"{key_folder}/{file_name_internal}",
            )
            items.append(s3_response["ContentDisposition"])
            items.append(s3_response["ContentType"])
            items.append(await s3_response["Body"].read())
        except ClientError as err:
            errname = err.response["Error"]["Message"]
            errcode = err.response["ResponseMetadata"]["HTTPStatusCode"]
            raise HTTPException(status_code=errcode, detail=errname)

    return items


async def s3_delete_file(key_name):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        try:
            object_exists = await s3.head_object(
                Bucket=settings.WASABI_BUCKET_NAME, Key=key_name
            )
            print(object_exists)
            delete = await s3.delete_object(
                Bucket=settings.WASABI_BUCKET_NAME, Key=key_name
            )
            print(delete)
            return True  # Deletion was successful
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False  # Deletion failed


async def upload_to_s3_for_presigned_url(file, bucket, key):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        file_content = await file.read()
        await s3.upload_fileobj(
            Fileobj=io.BytesIO(file_content),
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentDisposition": f"attachment; filename = {file.filename}"},
        )

        # Generate pre-signed URL and return it directly
        presigned_url = await s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
        return presigned_url


async def save_to_get_presigned_url(file: UploadFile, bucket: str, object_key: str):
    presigned_url = await upload_to_s3_for_presigned_url(file, bucket, object_key)
    return presigned_url  # Directly return the pre-signed URL


async def s3_presigned_url_from_key(bucket, key):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        # Generate pre-signed URL and return it directly
        presigned_url = await s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=600,
        )
        return presigned_url


async def s3_delete_all_files():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        try:
            # List all objects in the bucket
            objects_response = await s3.list_objects_v2(
                Bucket=settings.WASABI_BUCKET_NAME
            )
            if "Contents" in objects_response:
                for obj in objects_response["Contents"]:
                    # Delete each object
                    delete_response = await s3.delete_object(
                        Bucket=settings.WASABI_BUCKET_NAME, Key=obj["Key"]
                    )
                    print(f"Deleted {obj['Key']}: {delete_response}")
            return True  # Deletion of all objects was successful
        except ClientError as e:
            print(f"Error deleting objects: {e}")
            return False  # Deletion of objects failed


async def s3_delete_all_files_from_bucket(buket_name: str):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=settings.WASABI_API_BASE_URL,
        aws_access_key_id=settings.WASABI_ACCESS_KEY,
        aws_secret_access_key=settings.WASABI_SECRET_KEY,
    ) as s3:
        try:
            # List all objects in the bucket
            objects_response = await s3.list_objects_v2(Bucket=buket_name)
            if "Contents" in objects_response:
                for obj in objects_response["Contents"]:
                    # Delete each object
                    delete_response = await s3.delete_object(
                        Bucket=buket_name, Key=obj["Key"]
                    )
                    print(f"Deleted {obj['Key']}: {delete_response}")
            return True  # Deletion of all objects was successful
        except ClientError as e:
            print(f"Error deleting objects: {e}")
            return False  # Deletion of objects failed
