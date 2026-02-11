"""Base HTTP client with retry logic and rate limiting."""

import time
from typing import Any, Dict, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..utils.logger import LoggerMixin


class BaseAPIClient(LoggerMixin):
    """Base class for API clients with retry and rate limiting."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize base client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Configure session with default headers."""
        self.session.headers.update({"User-Agent": "ImageFetcherBot/1.0"})
        if self.api_key:
            self._add_auth_header()

    def _add_auth_header(self) -> None:
        """Add authentication header. Override in subclasses."""
        pass

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=2, max=60),
           retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)))
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self.logger.debug(f"{method.upper()} {url}")
        
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            self.logger.warning(f"Rate limited. Waiting {retry_after}s")
            time.sleep(retry_after)
            response = self.session.request(method, url, **kwargs)
        
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None,
             json: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
        """POST request."""
        return self._request("POST", endpoint, data=data, json=json, files=files)

    def download_file(self, url: str) -> bytes:
        """Download file from URL."""
        self.logger.debug(f"Downloading {url}")
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        """Close session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
