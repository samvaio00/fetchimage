#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test of API keys without complex imports."""

import os
import sys
import requests
from dotenv import load_dotenv

# Set console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")

# Load .env file
load_dotenv()

def test_freepik():
    """Test Freepik API."""
    api_key = os.getenv("FREEPIK_API_KEY")
    if not api_key:
        print("[!] Freepik: No API key found")
        return False

    headers = {"x-freepik-api-key": api_key}
    params = {"term": "product", "limit": 1}

    try:
        response = requests.get(
            "https://api.freepik.com/v1/resources",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            print("[OK] Freepik API: Connected")
            return True
        else:
            print(f"[X] Freepik API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[X] Freepik API: {e}")
        return False


def test_pexels():
    """Test Pexels API."""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("[!] Pexels: No API key found")
        return False

    headers = {"Authorization": api_key}
    params = {"query": "product", "per_page": 1}

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            print("[OK] Pexels API: Connected")
            return True
        else:
            print(f"[X] Pexels API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[X] Pexels API: {e}")
        return False


def test_pixabay():
    """Test Pixabay API."""
    api_key = os.getenv("PIXABAY_API_KEY")
    if not api_key:
        print("[!] Pixabay: No API key found")
        return False

    params = {"key": api_key, "q": "product", "per_page": 3}

    try:
        response = requests.get(
            "https://pixabay.com/api/",
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            print("[OK] Pixabay API: Connected")
            return True
        else:
            print(f"[X] Pixabay API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[X] Pixabay API: {e}")
        return False


def test_wholesalehub():
    """Test WholesaleHub API."""
    api_url = os.getenv("REPLIT_API_URL")
    email = os.getenv("REPLIT_EMAIL")
    password = os.getenv("REPLIT_PASSWORD")

    if not all([api_url, email, password]):
        print("[!] WholesaleHub: Missing credentials")
        return False

    try:
        session = requests.Session()
        login_url = f"{api_url}/api/auth/login"
        payload = {"email": email, "password": password}

        response = session.post(login_url, json=payload, timeout=30)

        if response.status_code == 200 and "connect.sid" in session.cookies:
            print("[OK] WholesaleHub API: Authenticated")
            return True
        else:
            print(f"[X] WholesaleHub API: Auth failed - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[X] WholesaleHub API: {e}")
        return False


def main():
    print("\nTesting API Connections...")
    print("="*60)

    results = [
        test_freepik(),
        test_pexels(),
        test_pixabay(),
        test_wholesalehub()
    ]

    print("="*60)
    success = sum(results)
    total = len(results)

    if success == total:
        print(f"\n[OK] All {total} APIs working!\n")
        return 0
    else:
        print(f"\n[!] {success}/{total} APIs working\n")
        return 1


if __name__ == "__main__":
    exit(main())
