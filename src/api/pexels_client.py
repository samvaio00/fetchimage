"""Pexels API client."""

from typing import List
from .base_client import BaseAPIClient
from ..storage.models import ImageResult, ImageSource


class PexelsClient(BaseAPIClient):
    """Client for Pexels API."""

    def __init__(self, api_key: str):
        """Initialize Pexels client."""
        super().__init__(base_url="https://api.pexels.com/v1", api_key=api_key)

    def _add_auth_header(self) -> None:
        """Add Pexels authorization header."""
        self.session.headers.update({"Authorization": self.api_key})

    def search_images(self, query: str, per_page: int = 5, size: str = "medium") -> List[ImageResult]:
        """Search for images on Pexels."""
        self.logger.info(f"Searching Pexels for: {query}")
        
        params = {"query": query, "per_page": per_page, "size": size}
        response = self.get("/search", params=params)
        data = response.json()
        
        results = []
        for item in data.get("photos", []):
            results.append(ImageResult(
                id=str(item["id"]),
                url=item["src"]["large"],
                download_url=item["src"]["original"],
                source=ImageSource.PEXELS,
                title=item.get("alt") or query,
                width=item["width"],
                height=item["height"],
                photographer=item["photographer"],
                photographer_url=item["photographer_url"]
            ))
        
        self.logger.info(f"Found {len(results)} images on Pexels")
        return results
