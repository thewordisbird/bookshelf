
import requests
import json
def get_book(book_id):
    #endpoint = f"https://www.googleapis.com/books/v1/volumes?q={search_data.replace(' ', '+')}"
    endpoint = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    resp = requests.get(endpoint, headers=headers)
    return resp.json()

