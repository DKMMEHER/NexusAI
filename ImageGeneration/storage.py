from abc import ABC, abstractmethod
import os
import logging
import base64

logger = logging.getLogger("Storage")

class StorageProvider(ABC):
    @abstractmethod
    def save_image(self, b64_data: str, job_id: str) -> str:
        """Saves an image and returns its web-accessible path/URL."""
        pass

class LocalStorage(StorageProvider):
    def __init__(self, base_dir: str = "Generated_Images"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_image(self, b64_data: str, job_id: str) -> str:
        try:
            image_data = base64.b64decode(b64_data)
            filename = f"{job_id}.png"
            filepath = os.path.join(self.base_dir, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)
            # Return relative web path matching frontend expectation
            return f"/image/images/{filename}"
        except Exception as e:
            logger.error(f"Failed to save image to disk: {e}")
            return ""

class GoogleCloudStorage(StorageProvider):
    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Initialized GoogleCloudStorage with bucket: {bucket_name}")

    def save_image(self, b64_data: str, job_id: str) -> str:
        try:
            image_data = base64.b64decode(b64_data)
            filename = f"{job_id}.png"
            blob = self.bucket.blob(f"images/{filename}")
            blob.upload_from_string(image_data, content_type="image/png")
            logger.info(f"Uploaded image to gs://{self.bucket_name}/images/{filename}")
            
            # Return Proxy URL (Relative path handled by frontend/networking)
            return f"/image/gcs/{filename}"
        except Exception as e:
            logger.error(f"Failed to upload image to GCS: {e}")
            return ""
