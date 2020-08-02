import requests


def get_book(book_id):
    """Query Google Book API for book item by ID.

    Args:
        book_id (str): Id for the book.
    """
    endpoint = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    resp = requests.get(endpoint, headers=headers)
    book = resp.json()
    return thumbnail_to_https(book)


def get_books(query, max_results=25):
    """Query Google Book API for books by search query.

    Args:
        query (str): Search query (Author, Title, ISBN, etc.).
        max_results (int): Number of items to return. Default set to 25.

    """
    endpoint = f"https://www.googleapis.com/books/v1/volumes/?q={query}&Type=books&maxResults={max_results}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    resp = requests.get(endpoint, headers=headers)
    books = resp.json()["items"]
    return list(map(thumbnail_to_https, books))


def thumbnail_to_https(book):
    """Modifies cover thumbnail url from http:// to https://"""
    if (
        "imageLinks" in book["volumeInfo"] and "thumbnail" in book["volumeInfo"]["imageLinks"]
    ):
        thumbnail_url = book["volumeInfo"]["imageLinks"]["thumbnail"]
        if thumbnail_url[4] != "s":
            book["volumeInfo"]["imageLinks"]["thumbnail"] = (
                thumbnail_url[:4] + "s" + thumbnail_url[4:]
            )

    return book
