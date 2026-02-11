"""Unsplash API client."""

from typing import List
from .base_client import BaseAPIClient
from ..storage.models import ImageResult, ImageSource


class UnsplashClient(BaseAPIClient):
    """Client for Unsplash API."""

    def __init__(self, access_key: str):
        """Initialize Unsplash client."""
        super().__init__(base_url="https://api.unsplash.com", api_key=access_key)

    def _add_auth_header(self) -> None:
        """Add Unsplash authorization header."""
        self.session.headers.update({"Authorization": f"Client-ID {self.api_key}"})

    def search_images(self, query: str, per_page: int = 5, orientation: str = "landscape") -> List[ImageResult]:
        """Search for images on Unsplash."""
        self.logger.info(f"Searching Unsplash for: {query}")
        
        params = {"query": query, "per_page": per_page, "orientation": orientation}
        response = self.get("/search/photos", params=params)
        data = response.json()
        
        results = []
        for item in data.get("results", []):
            results.append(ImageResult(
                id=item["id"],
                url=item["urls"]["regular"],
                download_url=item["urls"]["full"],
                source=ImageSource.UNSPLASH,
                title=item.get("alt_description") or item.get("description") or query,
                width=item["width"],
                height=item["height"],
                photographer=item["user"]["name"],
                photographer_url=item["user"]["links"]["html"]
            ))
        
        self.logger.info(f"Found {len(results)} images on Unsplash")
        return results
