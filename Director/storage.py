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
    def __init__(self, base_dir: str = "Generated_Video", base_url: str = "http://127.0.0.1:8006/videos"):
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
