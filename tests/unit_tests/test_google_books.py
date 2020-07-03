import pytest
from bookshelf.google_books import get_book, get_books

@pytest.mark.parametrize('book_id, title', 
                        [
                            ('6e4cDvhrKhgC', 'Steve Jobs'),
                            ('CGVDDwAAQBAJ', 'Where the Crawdads Sing')
                        ])
def test_get_book(book_id, title):
    # WHEN get_book is passed a book_id
    # THEN get_book will return a json response with the book data
    book = get_book(book_id)
    assert book['volumeInfo']['title'] == title

@pytest.mark.parametrize('query', 
                        [
                            ('Steve Jobs')
                        ])
def test_get_books(query):
    # WHEN get_books is passed a search query
    # THEN get_books will return the first 25 (default value) items results
    books = get_books(query)
    assert len(books['items']) == 25

@pytest.mark.parametrize('query, max_results', 
                        [
                            ('Steve Jobs', 5),
                            ('Economics', 25)
                        ])
def test_get_books_max_results(query, max_results):
    # WHEN get_books is passed a search query and max_results amount
    # THEN get_books will return the number of results requested
    books = get_books(query, max_results)
    assert len(books['items']) == max_results