from abc import ABC, abstractmethod

class IFileStorageStrategy(ABC):
    """
    Abstract interface for file storage strategies (Strategy Pattern).
    Defines methods to store and delete documents in a tenant-isolated manner.
    """
    
    @abstractmethod
    def store(self, file_content: bytes, filename: str, tenant_id: str) -> str:
        """
        Stores the given file contents.
        Returns the resolved URL or path representing the stored file.
        """
        pass

    @abstractmethod
    def delete(self, file_url: str) -> None:
        """
        Deletes the file corresponding to the specified URL or path.
        """
        pass
