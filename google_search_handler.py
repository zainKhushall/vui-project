import requests

def google_custom_search(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": 'your-key',
        "cx": '1504deb7f763947f6',
        "q": query
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
