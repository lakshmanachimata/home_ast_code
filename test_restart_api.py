#!/usr/bin/env python3
"""Test script to call the restart API and verify it works."""
import requests
import sys
import time

def test_restart(access_token: str):
    """Test the restart API."""
    url = "http://localhost:8123/api/services/homeassistant/restart"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("Calling restart API...")
    try:
        response = requests.post(url, headers=headers, json={}, timeout=5)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✓ Restart API call successful!")
            print("Home Assistant should now exit with code 100 and restart.")
            print("Check the terminal running run_with_restart.sh to see the restart.")
        else:
            print(f"\n✗ Restart API call failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to Home Assistant.")
        print("Make sure Home Assistant is running on http://localhost:8123")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_restart_api.py <access_token>")
        print("\nTo get an access token:")
        print("1. Go to http://localhost:8123")
        print("2. Profile → Long-Lived Access Tokens → Create Token")
        sys.exit(1)
    
    access_token = sys.argv[1]
    test_restart(access_token)

