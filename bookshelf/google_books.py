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
    book = resp.json()
    return thumbnail_to_https(book)

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
    books = resp.json()['items']
    #print(type(books))
    #print(books)
    return list(map(thumbnail_to_https,books))


def thumbnail_to_https(book):
    if 'imageLinks' in book['volumeInfo'] and 'thumbnail' in book['volumeInfo']['imageLinks']:
        thumbnail_url = book['volumeInfo']['imageLinks']['thumbnail']
        print(thumbnail_url)
        if thumbnail_url[4] != 's':
            book['volumeInfo']['imageLinks']['thumbnail'] = \
                thumbnail_url[:4] + 's' + thumbnail_url[4:]
                
    return book