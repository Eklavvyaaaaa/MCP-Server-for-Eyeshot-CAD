import argparse
import requests
import sys
import json

API_URL = "http://localhost:8000/command"

def main():
    parser = argparse.ArgumentParser(description="Test CLI for MCP CAD Server")
    parser.add_argument("prompt", type=str, help="Natural language CAD command")
    
    args = parser.parse_args()
    
    print(f"Sending prompt: '{args.prompt}'")
    
    try:
        response = requests.post(API_URL, json={"prompt": args.prompt})
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nFailed to connect to the MCP CAD Server.")
        print("Make sure it's running via: uvicorn app.main:app --reload")
        sys.exit(1)

if __name__ == "__main__":
    main()