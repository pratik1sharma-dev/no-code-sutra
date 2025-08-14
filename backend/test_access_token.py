#!/usr/bin/env python3
"""
Test script to check access token resolution
"""

import os


def main():
    print("🔐 Access token check")
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    if token:
        print("✅ INSTAGRAM_ACCESS_TOKEN is set")
        return True
    else:
        print("ℹ️  INSTAGRAM_ACCESS_TOKEN not set (simulation mode will be used)")
        return True


if __name__ == "__main__":
    main()
