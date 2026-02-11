"""Freepik API client."""

from typing import List
from src.api.base_client import BaseAPIClient
from src.storage.models import ImageResult, ImageSource


class FreepikClient(BaseAPIClient):
    """Client for Freepik API."""

    def __init__(self, api_key: str):
        """Initialize Freepik client."""
        super().__init__(base_url="https://api.freepik.com/v1", api_key=api_key)

    def _add_auth_header(self) -> None:
        """Add Freepik authorization header."""
        self.session.headers.update({"x-freepik-api-key": self.api_key})

    def search_images(self, query: str, per_page: int = 5) -> List[ImageResult]:
        """Search for images on Freepik.

        Args:
            query: Search query string
            per_page: Number of results to return (default: 5)

        Returns:
            List of ImageResult objects
        """
        self.logger.info(f"Searching Freepik for: {query}")

        params = {
            "term": query,
            "limit": per_page
        }

        try:
            response = self.get("/resources", params=params)
            data = response.json()

            results = []
            for item in data.get("data", []):
                # Freepik API structure
                image_data = item.get("image", {})
                thumbnail = image_data.get("thumbnail", {})

                results.append(ImageResult(
                    id=str(item.get("id", "")),
                    url=thumbnail.get("url", ""),
                    download_url=image_data.get("source", {}).get("url", thumbnail.get("url", "")),
                    source=ImageSource.FREEPIK,
                    title=item.get("title", query),
                    width=thumbnail.get("width", 800),
                    height=thumbnail.get("height", 600),
                    photographer=item.get("author", {}).get("name", "Unknown"),
                    photographer_url=item.get("author", {}).get("url", "")
                ))

            self.logger.info(f"Found {len(results)} images on Freepik")
            return results

        except Exception as e:
            self.logger.error(f"Freepik API error: {e}")
            return []
