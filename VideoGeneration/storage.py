from abc import ABC, abstractmethod
import os
import shutil
import logging

logger = logging.getLogger("Storage")

class StorageProvider(ABC):
    @abstractmethod
    def save_video(self, source_data: bytes, filename: str) -> str:
        """Saves video bytes and returns its access path/URL."""
        pass
        
    @abstractmethod
    def save_video_from_path(self, source_path: str, filename: str) -> str:
        """Saves a video file from path and returns its access path/URL."""
        pass

    @abstractmethod
    def get_video_url(self, filename: str) -> str:
        """Returns the public access URL for a given filename."""
        pass

class LocalStorage(StorageProvider):
    def __init__(self, base_dir: str = "Generated_Videos", base_url: str = "/Generated_Videos"):
        self.base_dir = os.path.abspath(base_dir)
        self.base_url = base_url
        os.makedirs(self.base_dir, exist_ok=True)

    def save_video(self, source_data: bytes, filename: str) -> str:
        target_path = os.path.join(self.base_dir, filename)
        try:
            with open(target_path, "wb") as f:
                f.write(source_data)
            logger.info(f"Saved video bytes to: {target_path}")
        except Exception as e:
            logger.error(f"Failed to save video bytes: {e}")
            raise e
        return f"{self.base_url}/{filename}"

    def save_video_from_path(self, source_path: str, filename: str) -> str:
        target_path = os.path.join(self.base_dir, filename)
        
        # If already there
        if os.path.abspath(source_path) == os.path.abspath(target_path):
             return f"{self.base_url}/{filename}"
             
        try:
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied video to: {target_path}")
        except Exception as e:
            logger.error(f"Failed to copy video: {e}")
            raise e
        return f"{self.base_url}/{filename}"

    def get_video_url(self, filename: str) -> str:
        return f"{self.base_url}/{filename}"

class GoogleCloudStorage(StorageProvider):
    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Initialized GoogleCloudStorage with bucket: {bucket_name}")

    def save_video(self, source_data: bytes, filename: str) -> str:
        blob = self.bucket.blob(f"videos/{filename}")
        blob.upload_from_string(source_data, content_type="video/mp4")
        logger.info(f"Uploaded video bytes to gs://{self.bucket_name}/videos/{filename}")
        return f"https://storage.googleapis.com/{self.bucket_name}/videos/{filename}"

    def save_video_from_path(self, source_path: str, filename: str) -> str:
        blob = self.bucket.blob(f"videos/{filename}")
        blob.upload_from_filename(source_path)
        logger.info(f"Uploaded video file to gs://{self.bucket_name}/videos/{filename}")
        return f"https://storage.googleapis.com/{self.bucket_name}/videos/{filename}"

    def get_video_url(self, filename: str) -> str:
        return f"https://storage.googleapis.com/{self.bucket_name}/videos/{filename}"
