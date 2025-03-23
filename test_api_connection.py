import requests
import json
import sys

def test_api_connection():
    """Test if the Flask API is running and accessible."""
    print("Testing API connection to http://localhost:5000/api/health")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API is running!")
            try:
                data = response.json()
                print(f"API response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"⚠️ WARNING: Response is not valid JSON: {response.text}")
                return False
        else:
            print(f"❌ ERROR: API returned status code {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API. Make sure the Flask server is running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Connection to API timed out. Server might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Make sure you're in the correct directory (TestForge)")
        print("2. Make sure Flask is installed: pip install flask flask-cors")
        print("3. Check if port 5000 is already in use by another application")
        print("4. Try running the Flask server with: python app.py")
        print("5. Check if your firewall is blocking connections to port 5000")
        sys.exit(1)
    else:
        print("\nAPI is running correctly!")
        sys.exit(0) 