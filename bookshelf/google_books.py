import requests
import json

def get_book(book_id):
    """
    Query Google Book API for book item by ID.

    Args: 
        book_id: Id for the book.
    """
    endpoint = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    resp = requests.get(endpoint, headers=headers)
    return resp.json()

def get_books(query, max_results=25):
    """
    Query Google Book API for books by search query.

    Args:
        query: String search query.
        max_results: Number of items to return. 25 by default.
    """
    endpoint = f'https://www.googleapis.com/books/v1/volumes/?q={query}&Type=books&maxResults={max_results}'
    headers = {"content-type": "application/json; charset=UTF-8"}
    resp = requests.get(endpoint, headers=headers)
    return resp.json()