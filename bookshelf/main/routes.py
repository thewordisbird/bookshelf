from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, request, jsonify, json, url_for, session

from .forms import SearchForm, ReviewForm
from .google_books import get_book
from bookshelf.firebase_auth import login_required
from bookshelf.firebase_firestore import set_reading, get_reading_doc, set_read, remove_reading_doc, get_read_doc, get_reviews, get_user

from bookshelf.firebase_objects import Book
bp = Blueprint('books', __name__)

def clean_form_data(data):
    """Remove CSRF From form data, convert rating to number"""
    del data['csrf_token']
    if 'rating' in data:
        data['rating'] = int(data['rating'])
    return data

@bp.route('/')
def index():
    return ('<p>You are at the index</p>')

# /user routes
@bp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile(user_id):
    session_cookie = request.cookies.get('firebase')
    user = session['_user']
    #print(user)
    #reading = get_books(user['id'], 'currently_reading')``
    #read = get_books(user['id'], 'read')
    return render_template('profile.html', user=user)

# /books routes
@bp.route('/books/search', methods=['GET'])
def search():
    form = SearchForm()
    return render_template('search.html', title='Find A Book', form=form)

@bp.route('/books/<book_id>', methods=['GET'])
def book_details(book_id):
    book = get_book(book_id)
    if '_user' in session:
        
        book_user_info = Book.build_from_db(session['_user']['uid'], book_id)
        book_user_info.date_rated = datetime.now()
        #print(f'book_user_info:\n {book_user_info.__dict__}\n')
    else:
        book_user_info = None
    book_reviews = Book.get_all_reviews(book_id)
    print(book_reviews)
    return render_template('book_details.html', book=book, book_user_info=book_user_info, book_reviews=book_reviews)

@bp.route('/books/review/new/<book_id>', methods=['GET', 'POST'])
def new_review(book_id):
    rating = request.args.get('rating', 0)
    form = ReviewForm(rating = request.args.get('rating'))
    #print(form.data)
    #print(form.validate())
    #print(form.errors)
    if form.validate_on_submit():
        book = Book(session['_user']['uid'], book_id, form.data)
        book.date_rated = datetime.now()
        #print('book', book.__dict__)
        book.write_to_db()
        return redirect(url_for('books.book_details', book_id=book_id))
    
    book = get_book(book_id)
    book_user_info = Book.build_from_db(session['_user']['uid'], book_id)

    if book_user_info.date_started:
        form.date_started.data = book_user_info.date_started

    #print(form.data)
    return render_template('review_form.html', form=form, book=book, rating=int(rating))

# REST Requests
@bp.route('/reading', methods=['POST'])
def reading():
    book_id = request.form.get('bookId')
    try:
        #print(session['_user']['uid'])
        book = Book(session['_user']['uid'], book_id, {'date_started': datetime.now()})
        book.write_to_db()
        
    except Exception as e:
        #print(e)
        resp = jsonify({'status': 'unable to process request'})
    else:
        resp = jsonify({'status': 'success', 'startDate': book.date_started.strftime('%m/%d/%y')})
    return resp
