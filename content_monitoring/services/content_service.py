from content_monitoring.services.scan_service import ScanService


class ContentService:
    """Service layer for content-related workflows."""

    def __init__(self, scan_service: ScanService | None = None) -> None:
        self.scan_service = scan_service or ScanService()

    def scan_dataset(self, dataset_path: str | None = None) -> dict:
        return self.scan_service.scan_dataset(dataset_path=dataset_path)
