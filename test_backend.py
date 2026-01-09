#!/usr/bin/env python3
"""
Quick test script to verify backend is running and accessible
"""
import requests
import sys
import time

BACKEND_URL = "http://localhost:5000/api"

def test_backend():
    print("🔍 Testing Backend Connection...")
    print("=" * 60)
    
    # Test status endpoint
    try:
        print(f"📡 Connecting to {BACKEND_URL}/status...")
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Backend: {data.get('backend', 'unknown')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            if 'face_mesh_ready' in data:
                print(f"   Face Mesh: {'✅ Ready' if data['face_mesh_ready'] else '❌ Not ready'}")
            print("=" * 60)
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server is not running")
        print("💡 Start the backend with: cd backend && python server.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Backend took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_backend()
    print("\n")
    
    if not success:
        print("💡 Troubleshooting Steps:")
        print("   1. Make sure backend server is running")
        print("   2. Check if port 5000 is available")
        print("   3. Verify Python dependencies are installed")
        print("   4. Check backend/server.py for errors")
        print("\n")
        sys.exit(1)
    else:
        print("✅ All tests passed! Backend is ready.")
        sys.exit(0)
