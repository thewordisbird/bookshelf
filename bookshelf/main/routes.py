
from flask import Flask, Blueprint, render_template, redirect, request, jsonify, json, url_for, session

from .forms import SearchForm, ReviewForm
from .google_books import get_book
from bookshelf.firebase_auth import login_required
from bookshelf.firebase_firestore import set_reading, get_reading_doc, set_read, remove_reading_doc, get_read_doc, get_reviews, get_user

bp = Blueprint('books', __name__)


        

def clean_form_data(data):
    """Remove CSRF From form data, convert rating to number"""
    del data['csrf_token']
    if 'rating' in data:
        data['rating'] = int(data['rating'])
    return data

@bp.route('/index')
def index():
    return ('<p>You are at the index</p>')

@bp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile(user_id):
    session_cookie = request.cookies.get('firebase')
    user = get_user(session['_user_id'])
    
    #reading = get_books(user['id'], 'currently_reading')
    #read = get_books(user['id'], 'read')
    return render_template('profile.html', user=user)

@bp.route('/search', methods=['GET'])
@login_required
def search():
    form = SearchForm()
    return render_template('search.html', title='Find A Book', form=form)

@bp.route('/book/<book_id>', methods=['GET'])
def book_details(book_id):
    book = get_book(book_id)
    reading = get_reading_doc(session['_user_id'], book_id)
    read = get_read_doc(session['_user_id'], book_id)
    reviews = get_reviews(book_id)
    #print(unescape(book['volumeInfo']['description']))
    return render_template('book_details.html', book=book, reading=reading, read=read, reviews=reviews)

@bp.route('/review/new/<book_id>', methods=['GET', 'POST'])
def new_review(book_id):
    form = ReviewForm()
    print(form.data)
    print(form.validate())
    print(form.errors)
    if form.validate_on_submit():
        data = clean_form_data(form.data)
        set_read(session['_user_id'], book_id, data)
        remove_reading_doc(session['_user_id'], book_id)
        return redirect(url_for('books.book_details', book_id=book_id))
    
    book = get_book(book_id)
    reading = get_reading_doc(session['_user_id'], book_id)

    if reading:
        form.date_started.data = reading['start_date']

    rating = request.args.get('rating')
    if rating:
        rating = int(rating)
    else:
        rating = 0
    #print(form.data)
    return render_template('review_form.html', form=form, book=book, rating=rating)

@bp.route('/reading', methods=['POST'])
def reading():
    book_id = request.form.get('bookId')
    try:
        book = set_reading(session['_user_id'], book_id)
        print(book)
    except Exception as e:
        print(e)
        resp = jsonify({'status': 'unable to process request'})
    else:
        resp = jsonify({'status': 'success', 'startDate': book['start_date'].strftime('%m/%d/%y')})
    return resp

@bp.route('/test')
def test():
    return ("<p>This is a test</p>")