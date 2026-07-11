import requests

def google_custom_search(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": 'AIzaSyBD1DhSgSIHDmVkYpD-iwSXPS_MW3xduDE',
        "cx": '1504deb7f763947f7',
        "q": query
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()