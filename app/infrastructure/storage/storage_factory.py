from app.infrastructure.storage.interface import IFileStorageStrategy
from app.infrastructure.storage.local_storage import LocalFileStorageStrategy

class FileStorageFactory:
    """
    Factory Method pattern to resolve the appropriate storage strategy for a given tenant.
    Currently returns the LocalFileStorageStrategy, but can be extended to yield other
    strategies (e.g., S3TenantIsolatedStorageStrategy) dynamically depending on tenant configurations.
    """
    
    @staticmethod
    def get_strategy(tenant_id: str) -> IFileStorageStrategy:
        # In this implementation we default to local storage.
        # Future enhancements could select S3/Cloud storage for specific tenants.
        return LocalFileStorageStrategy()
