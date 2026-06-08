import os
import uuid
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "production-media")


def upload_file_to_blob(file, folder_name: str) -> str:
    if not AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONNECTION_STRING == "your_azure_blob_connection_string":
        raise Exception("Azure Blob Storage is not configured. Add a valid connection string in .env.")

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )

    extension = file.filename.split(".")[-1]
    unique_filename = f"{folder_name}/{uuid.uuid4()}.{extension}"

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=unique_filename
    )

    blob_client.upload_blob(
        file.file,
        overwrite=True,
        content_settings=ContentSettings(
            content_type=file.content_type or "application/octet-stream"
        )
    )

    return blob_client.url