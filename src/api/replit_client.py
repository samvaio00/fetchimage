"""Replit API client for managing SKUs and images."""

from typing import List, Optional
from .base_client import BaseAPIClient
from ..storage.models import SKU


class ReplitClient(BaseAPIClient):
    """Client for Replit app REST API."""

    def __init__(self, api_url: str, api_key: str):
        """Initialize Replit client."""
        super().__init__(base_url=api_url, api_key=api_key)

    def _add_auth_header(self) -> None:
        """Add authorization header."""
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def get_skus_without_images(self, limit: int = 50) -> List[SKU]:
        """Get SKUs that don't have images attached."""
        self.logger.info(f"Fetching SKUs without images (limit: {limit})")
        
        params = {"has_image": "false", "limit": limit}
        response = self.get("/skus", params=params)
        data = response.json()
        
        skus = []
        for item in data.get("skus", []):
            skus.append(SKU(
                id=item["id"],
                name=item["name"],
                description=item.get("description"),
                category=item.get("category"),
                has_image=item.get("has_image", False)
            ))
        
        self.logger.info(f"Found {len(skus)} SKUs without images")
        return skus

    def attach_image_to_sku(self, sku_id: str, image_data: bytes, filename: str) -> bool:
        """Attach image to SKU."""
        self.logger.info(f"Attaching image to SKU {sku_id}")
        
        files = {"image": (filename, image_data, "image/jpeg")}
        response = self.post(f"/skus/{sku_id}/image", files=files)
        
        success = response.status_code in (200, 201)
        if success:
            self.logger.info(f"Successfully attached image to SKU {sku_id}")
        else:
            self.logger.error(f"Failed to attach image to SKU {sku_id}")
        
        return success

    def verify_image_attached(self, sku_id: str) -> bool:
        """Verify that image was successfully attached to SKU."""
        self.logger.debug(f"Verifying image for SKU {sku_id}")
        
        response = self.get(f"/skus/{sku_id}")
        data = response.json()
        
        return data.get("has_image", False)
