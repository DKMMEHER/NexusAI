from abc import ABC, abstractmethod
import os
import shutil
import logging

logger = logging.getLogger("Storage")

class StorageProvider(ABC):
    @abstractmethod
    def save_video(self, source_path: str, filename: str) -> str:
        """Saves a video file and returns its access path/URL."""
        pass

    @abstractmethod
    def get_video_url(self, filename: str) -> str:
        """Returns the public access URL for a given filename."""
        pass

class LocalStorage(StorageProvider):
    def __init__(self, base_dir: str = "Generated_Videos", base_url: str = "http://127.0.0.1:8006/videos"):
        self.base_dir = os.path.abspath(base_dir)
        self.base_url = base_url
        os.makedirs(self.base_dir, exist_ok=True)

    def save_video(self, source_path: str, filename: str) -> str:
        target_path = os.path.join(self.base_dir, filename)
        
        # If the file is already in the target directory (e.g. backend generated it there), just return
        if os.path.abspath(source_path) == os.path.abspath(target_path):
            logger.info(f"File already in place: {target_path}")
            return target_path
            
        try:
            shutil.move(source_path, target_path)
            logger.info(f"Moved video to: {target_path}")
        except Exception as e:
            logger.error(f"Failed to move video: {e}")
            raise e
            
        return target_path

    def get_video_url(self, filename: str) -> str:
        return f"{self.base_url}/{filename}"

class GoogleCloudStorage(StorageProvider):
    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Initialized GoogleCloudStorage with bucket: {bucket_name}")

    def save_video(self, source_path: str, filename: str) -> str:
        blob = self.bucket.blob(f"videos/{filename}")
        blob.upload_from_filename(source_path)
        logger.info(f"Uploaded video to gs://{self.bucket_name}/videos/{filename}")
        
        # Determine the public URL (assuming public access or signed URL needed later)
        # For now, returning the authenticated link or public link format
        # If the bucket is public: https://storage.googleapis.com/{bucket}/{blob_name}
        return f"https://storage.googleapis.com/{self.bucket_name}/videos/{filename}"

    def get_video_url(self, filename: str) -> str:
        return f"https://storage.googleapis.com/{self.bucket_name}/videos/{filename}"
