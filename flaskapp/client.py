import requests
import sys

try:
    # Проверяем, что сервер работает
    response = requests.get('http://localhost:500/', timeout = 5)
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        print("Server is working correctly")
        sys.exit(0)
    else:
        print(f"Server returned {response.status_code}")
        sys.exit(1)

except requests.exceptions.ConnectionError:
    print("Cannot connect to server")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
