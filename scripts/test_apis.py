#!/usr/bin/env python3
"""Test connectivity to all configured APIs."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import Config
from api.freepik_client import FreepikClient
from api.pexels_client import PexelsClient
from api.pixabay_client import PixabayClient
from api.replit_client import ReplitClient


def test_freepik(api_key: str):
    """Test Freepik API connection."""
    try:
        client = FreepikClient(api_key)
        results = client.search_images("test product", per_page=1)
        if results:
            print("✅ Freepik API: Connected")
            return True
        else:
            print("⚠️  Freepik API: Connected but no results")
            return True
    except Exception as e:
        print(f"❌ Freepik API: Failed - {e}")
        return False


def test_pexels(api_key: str):
    """Test Pexels API connection."""
    try:
        client = PexelsClient(api_key)
        results = client.search_images("test product", per_page=1)
        if results:
            print("✅ Pexels API: Connected")
            return True
        else:
            print("⚠️  Pexels API: Connected but no results")
            return True
    except Exception as e:
        print(f"❌ Pexels API: Failed - {e}")
        return False


def test_pixabay(api_key: str):
    """Test Pixabay API connection."""
    try:
        client = PixabayClient(api_key)
        results = client.search_images("test product", per_page=1)
        if results:
            print("✅ Pixabay API: Connected")
            return True
        else:
            print("⚠️  Pixabay API: Connected but no results")
            return True
    except Exception as e:
        print(f"❌ Pixabay API: Failed - {e}")
        return False


def test_wholesalehub(api_url: str, email: str, password: str):
    """Test WholesaleHub API connection."""
    try:
        client = ReplitClient(api_url, email, password)
        if client.authenticate():
            print("✅ WholesaleHub API: Authenticated")
            return True
        else:
            print("❌ WholesaleHub API: Authentication failed")
            return False
    except Exception as e:
        print(f"❌ WholesaleHub API: Failed - {e}")
        return False


def main():
    """Test all API connections."""
    print("\nTesting API connections...")
    print("="*60)

    try:
        config = Config()
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        print("\nMake sure you have:")
        print("  1. Created .env file with your API keys")
        print("  2. config/config.yaml exists")
        sys.exit(1)

    results = []

    # Test image APIs
    if config.env.freepik_api_key:
        results.append(test_freepik(config.env.freepik_api_key))
    else:
        print("⚠️  Freepik API: No API key configured")
        results.append(False)

    if config.env.pexels_api_key:
        results.append(test_pexels(config.env.pexels_api_key))
    else:
        print("⚠️  Pexels API: No API key configured")
        results.append(False)

    if config.env.pixabay_api_key:
        results.append(test_pixabay(config.env.pixabay_api_key))
    else:
        print("⚠️  Pixabay API: No API key configured")
        results.append(False)

    # Test WholesaleHub API
    results.append(test_wholesalehub(
        config.env.replit_api_url,
        config.env.replit_email,
        config.env.replit_password
    ))

    print("="*60)
    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        print(f"\n✅ All {total_count} APIs are working!\n")
        return 0
    else:
        print(f"\n⚠️  {success_count}/{total_count} APIs working\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
