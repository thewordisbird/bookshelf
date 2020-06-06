
from flask import Flask, Blueprint, render_template, request, jsonify, json

from .forms import SearchForm, ReviewForm
from .google_books import get_book
from html import unescape
bp = Blueprint('books', __name__)

@bp.route('/search', methods=['GET'])
def search():
    form = SearchForm()
    return render_template('search.html', title='Find A Book', form=form)

@bp.route('/book/<book_id>', methods=['GET'])
def book_details(book_id):
    book = get_book(book_id)
    #print(unescape(book['volumeInfo']['description']))
    return render_template('book_details.html', book=book)

@bp.route('/review/new/<book_id>', methods=['GET', 'POST'])
def new_review(book_id):
    form = ReviewForm()
    book = get_book(book_id)
    if form.validate_on_submit():
        pass

    return render_template('review_form.html', form=form, book=book)


@bp.route('/test')
def test():
    return ("<p>This is a test</p>")