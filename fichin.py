import requests

def post_token(username: str, password: str) -> dict:
    url = "https://api.invertironline.com/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()  # contiene el access_token y más info
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")