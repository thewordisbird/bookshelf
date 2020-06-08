
from flask import Flask, Blueprint, render_template, redirect, request, jsonify, json, url_for

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
    rating = request.args.get('rating')
    if rating:
        rating = int(rating)
    else:
        rating = 0
    print(rating)
    print(form.data)
    if form.validate_on_submit():
        print(form.data)
        return redirect(url_for('books.book_details', book_id=book_id))
    return render_template('review_form.html', form=form, book=book, rating=rating)


@bp.route('/test')
def test():
    return ("<p>This is a test</p>")