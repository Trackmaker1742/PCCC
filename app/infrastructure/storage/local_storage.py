import os
from app.infrastructure.storage.interface import IFileStorageStrategy
from app.config import STORED_FILES_DIR

class LocalFileStorageStrategy(IFileStorageStrategy):
    """
    Concrete storage strategy saving files to the local file system.
    Organizes files into tenant-specific subdirectories for data isolation.
    """
    
    def store(self, file_content: bytes, filename: str, tenant_id: str) -> str:
        # Construct tenant-isolated subfolder
        tenant_dir = os.path.join(STORED_FILES_DIR, tenant_id)
        os.makedirs(tenant_dir, exist_ok=True)
        
        # Save file to path
        file_path = os.path.join(tenant_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        # Return a relative URL path that our API server can serve static content from
        return f"/stored_files/{tenant_id}/{filename}"

    def delete(self, file_url: str) -> None:
        if not file_url:
            return
            
        # Parse path from URL
        # URL format: /stored_files/{tenant_id}/{filename}
        if file_url.startswith("/stored_files/"):
            path_parts = file_url.lstrip("/").split("/")
            if len(path_parts) >= 3:
                tenant_id = path_parts[1]
                filename = path_parts[2]
                
                # Resolve physical path
                file_path = os.path.join(STORED_FILES_DIR, tenant_id, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        print(f"Error deleting file {file_path}: {e}")
