"""Pixabay API client."""

from typing import List
from .base_client import BaseAPIClient
from ..storage.models import ImageResult, ImageSource


class PixabayClient(BaseAPIClient):
    """Client for Pixabay API."""

    def __init__(self, api_key: str):
        """Initialize Pixabay client."""
        super().__init__(base_url="https://pixabay.com/api", api_key=api_key)

    def search_images(self, query: str, per_page: int = 5, image_type: str = "photo") -> List[ImageResult]:
        """Search for images on Pixabay."""
        self.logger.info(f"Searching Pixabay for: {query}")
        
        params = {"key": self.api_key, "q": query, "per_page": per_page, 
                 "image_type": image_type, "safesearch": "true"}
        response = self.get("/", params=params)
        data = response.json()
        
        results = []
        for item in data.get("hits", []):
            results.append(ImageResult(
                id=str(item["id"]),
                url=item["webformatURL"],
                download_url=item["largeImageURL"],
                source=ImageSource.PIXABAY,
                title=item.get("tags") or query,
                width=item["imageWidth"],
                height=item["imageHeight"],
                photographer=item.get("user"),
                photographer_url=f"https://pixabay.com/users/{item.get('user')}-{item.get('user_id')}/"
                if item.get("user") else None
            ))
        
        self.logger.info(f"Found {len(results)} images on Pixabay")
        return results
