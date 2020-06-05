
import requests
import json
def get_book(volume_id):
    #endpoint = f"https://www.googleapis.com/books/v1/volumes?q={search_data.replace(' ', '+')}"
    endpoint = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
    resp = requests.get(endpoint)
    return resp.json()

