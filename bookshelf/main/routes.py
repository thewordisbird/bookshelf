from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, request, jsonify, json, url_for, session

from .forms import SearchForm, ReviewForm
from .google_books import get_book
from bookshelf.firebase_auth import login_required
from bookshelf.firebase_firestore import set_reading, get_reading_doc, set_read, remove_reading_doc, get_read_doc, get_reviews, get_user

from bookshelf.firebase_objects import User, Book
bp = Blueprint('books', __name__)


@bp.route('/')
def index():
    return ('<p>You are at the index</p>')

# /user routes
@bp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile(user_id):
    user = User(session['_user'])
    books = user.get_books()
    print(f'user:\n{user.__dict__}\n')
    print(f'books:\n{books}\n')
    return render_template('profile.html', user=user, books=books)


@bp.route('/profile/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = User(session['_user'])
    form = EditProfile(data=user.__dict__)

    if form.validate_on_submit():
        update_data = {}
        for k,v in user.__dict__.items():
            if k in form.data:
                if form.data[k] != v:
                    update_data[k] = form.data[k]
        user.update_db(update_data)

        session['_user'] = user.__dict__
        return redirect(url_for('profile', user_id=user.uid))
    return render_template('edit_profile_form', form=form)


# /books routes
@bp.route('/books/search', methods=['GET'])
def search():
    form = SearchForm()
    return render_template('search.html', title='Find A Book', form=form)

@bp.route('/books/<book_id>', methods=['GET'])
def book_details(book_id):
    book = get_book(book_id)
    book_user_info = None
    if '_user' in session:
        book_user_info = Book.build_from_db(session['_user']['uid'], book_id)
        print(f'book_user_info:\n {book_user_info.__dict__}\n')
       
    book_reviews = Book.get_all_reviews(book_id)
    #print(f'book reviews:\n {book_reviews}\n')
    return render_template('book_details.html', book=book, book_user_info=book_user_info, book_reviews=book_reviews)

@bp.route('/books/review/new/<book_id>', methods=['GET', 'POST'])
@login_required
def new_review(book_id):
    rating=request.args.get('rating', 0)
    form = ReviewForm(rating=rating)
    book = get_book(book_id)
    #print(form.data)
    #print(form.validate())
    #print(form.errors)
    if form.validate_on_submit():
        data = {
            'uid': session['_user']['uid'],
            'display_name': session['_user']['display_name'],
            'bid': book_id,
            'title': book['volumeInfo']['title'],
            'authors': book['volumeInfo']['authors'],
            'cover_url': book['volumeInfo']['imageLinks']['thumbnail'],
            'date_rated': datetime.now()
        }
        data.update(form.data)
        print(data)
        book = Book(data)
        print('book', book.__dict__)
        book.write_to_db()
        return redirect(url_for('books.book_details', book_id=book_id))

    book_user_info = Book.build_from_db(session['_user']['uid'], book_id)

    if 'date_started' in book_user_info.__dict__:
        form.date_started.data = book_user_info.date_started
    #print(form.data)
    return render_template('review_form.html', form=form, book=book, rating=int(rating))

# REST Requests
@bp.route('/reading', methods=['POST'])
def reading():
    book_id = request.form.get('bookId')
    book = get_book(book_id)
    data = {
        'uid': session['_user']['uid'],
        'display_name': session['_user']['display_name'],
        'bid': request.form.get('bookId'),
        'title': book['volumeInfo']['title'],
        'authors': book['volumeInfo']['authors'],
        'cover_url': book['volumeInfo']['imageLinks']['thumbnail'],
        'date_started': datetime.now()
    }
    try:
        #print(session['_user']['uid'])
        book = Book(data)
        book.write_to_db()
        
    except Exception as e:
        #print(e)
        resp = jsonify({'status': 'unable to process request'})
    else:
        resp = jsonify({'status': 'success', 'startDate': book.date_started.strftime('%m/%d/%y')})
    return resp
