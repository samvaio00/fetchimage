"""WholesaleHub Replit API client with session-based authentication."""

from typing import List, Optional
import requests
from src.storage.models import SKU
from src.utils.logger import LoggerMixin


class ReplitClient(LoggerMixin):
    """Client for WholesaleHub Replit app REST API.
    
    API Documentation: https://warnergears.replit.app
    Authentication: Session-based (login to get connect.sid cookie)
    """

    def __init__(self, api_url: str, email: str, password: str):
        """Initialize Replit client with session authentication.
        
        Args:
            api_url: Base URL (https://warnergears.replit.app)
            email: Admin email for login
            password: Admin password for login
        """
        self.base_url = api_url.rstrip("/")
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ImageFetcherBot/1.0"})
        self._authenticated = False

    def authenticate(self) -> bool:
        """Login to get session cookie.
        
        Returns:
            True if authentication successful
        """
        self.logger.info(f"Authenticating with {self.base_url}")
        
        login_url = f"{self.base_url}/api/auth/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = self.session.post(login_url, json=payload, timeout=30)
            response.raise_for_status()
            
            # Check if we got the connect.sid cookie
            if "connect.sid" in self.session.cookies:
                self._authenticated = True
                self.logger.info("Authentication successful - session cookie obtained")
                return True
            else:
                self.logger.error("Authentication failed - no session cookie received")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid session, re-authenticate if needed."""
        if not self._authenticated:
            if not self.authenticate():
                raise RuntimeError("Failed to authenticate with Replit API")

    def get_skus_without_images(self, limit: int = 50) -> List[SKU]:
        """Get SKUs that don't have images attached.
        
        Note: This endpoint needs to be implemented on the Replit side.
        For now, this is a placeholder that returns empty list.
        
        TODO: Update this once the Replit API provides an endpoint to list products.
        """
        self._ensure_authenticated()
        
        self.logger.warning("get_skus_without_images not implemented in Replit API yet")
        self.logger.info("You'll need to provide SKU list manually or implement product listing endpoint")
        
        # Placeholder - in reality you'd call something like:
        # response = self.session.get(f"{self.base_url}/api/admin/products?hasImage=false&limit={limit}")
        # data = response.json()
        # return [SKU(...) for item in data["products"]]
        
        return []

    def attach_image_to_sku(self, sku: str, image_data: bytes, filename: str) -> bool:
        """Upload image for a specific SKU.
        
        Args:
            sku: Product SKU (case-insensitive)
            image_data: Image file bytes
            filename: Image filename (for content type detection)
        
        Returns:
            True if upload successful
        """
        self._ensure_authenticated()
        
        self.logger.info(f"Uploading image for SKU: {sku}")
        
        upload_url = f"{self.base_url}/api/admin/products/upload-image"
        
        # Determine content type from filename
        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            content_type = "image/webp"
        
        files = {
            "image": (filename, image_data, content_type)
        }
        
        data = {
            "sku": sku
        }
        
        try:
            response = self.session.post(upload_url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.logger.info(f"Successfully uploaded image for SKU {sku}")
                    self.logger.debug(f"Saved as: {result.get('filename')}")
                    return True
                else:
                    self.logger.error(f"Upload failed for SKU {sku}: {result.get('message')}")
                    return False
                    
            elif response.status_code == 404:
                self.logger.warning(f"Product not found for SKU: {sku}")
                return False
                
            elif response.status_code in (401, 403):
                self.logger.warning("Session expired, re-authenticating...")
                self._authenticated = False
                self._ensure_authenticated()
                # Retry once after re-auth
                return self.attach_image_to_sku(sku, image_data, filename)
                
            elif response.status_code == 400:
                self.logger.error(f"Bad request for SKU {sku}: {response.text}")
                return False
                
            else:
                self.logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for SKU {sku}: {e}")
            return False

    def verify_image_attached(self, sku: str) -> bool:
        """Verify that image was successfully attached to SKU.
        
        Note: This endpoint needs to be implemented on the Replit side.
        For now, we rely on the upload response.
        """
        self.logger.debug(f"Image verification not implemented - relying on upload response")
        return True

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
