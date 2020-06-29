from datetime import datetime
from flask import Blueprint, render_template, redirect, request, \
    jsonify, url_for, session

# API's
from .forms import SearchForm, ReviewForm
from bookshelf.google_books_api import get_book, get_books
from bookshelf.firebase_auth import login_required

from bookshelf.firebase_objects import User, Book
bp = Blueprint('books', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    # -- UPDATE --
    # books = get_collection_group("books", order_by=("last_updated", "DECENDING"))
    # -- END UPDATE -- 

    books = Book.get_all_books()
    return render_template('index.html', title="bookshelf | home", books=books)

# /user routes
@bp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile(user_id):
    # -- UPDATE --
    # user = firebase.get_document(f"users/{user_id}")
    # books = firebase.get_collection(f"users/{user_id}/books")
    # -- END UPDATE --

    user = User.build_from_db(user_id)
    books = user.get_books()
    print(f'user:\n{user.__dict__}\n')
    print(f'books:\n{books}\n')
    return render_template('profile.html', title=f"bookshelf | {user.display_name}", user=user, books=books)


@bp.route('/profile/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    # Not Yet Implemented
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
    # Import google_books_api and call google_books_api.get_books()
    books= get_books(request.args.get('q'))['items']
    print(books)
    return render_template('search.html', title='bookshelf | Search', books=books)

@bp.route('/books/<book_id>', methods=['GET'])
@login_required
def book_details(book_id):
    book = get_book(book_id)
    book_user_info = None
    if '_user' in session:
        # -- UPDATE --
        # book_user_info = firestore.get_document(f"users/{session['_user']['uid']}/books/{book_id}")
        # -- END UPDATE

        book_user_info = Book.build_from_db(session['_user']['uid'], book_id)
        print(f'book_user_info:\n {book_user_info.__dict__}\n')
    
    # -- UPDATE --
    # book_reviews = firestore.get_collection_group("books", where=("bid", "==", book_id))
    # -- END UPDATE

    book_reviews = Book.get_all_reviews(book_id)
    #print(f'book reviews:\n {book_reviews}\n')
    return render_template('book_details.html', title=f"bookshelf | {book['volumeInfo']['title']}", book=book, book_user_info=book_user_info, book_reviews=book_reviews)

@bp.route('/books/review/new/<book_id>', methods=['GET', 'POST'])
@login_required
def new_review(book_id):
    rating=request.args.get('rating', 0)
    form = ReviewForm(rating=rating)
    book = get_book(book_id)
    print(form.data)
    print(form.validate())
    print(form.errors)
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
        # -- UPDATE --
        # need cloud function for logging update and write times
        # book = firestore.set_document(f"users/{data['uid']}/books/{data['bid']}", data)
        # -- END UPDATE --
        
        print(data)
        book = Book(data)
        print('book', book.__dict__)
        book.write_to_db()
        return redirect(url_for('books.book_details', book_id=book_id))

    # -- UPDATE --
    # book_user_info = firestore.get_document(f"users/{session['_user']['uid']}/books/{book_id}")
    # if 'date_started' in book_user_info:
    #    form.date_started.data = book_user_info.date_started
    # -- END UPDATE --

    book_user_info = Book.build_from_db(session['_user']['uid'], book_id)

    if 'date_started' in book_user_info.__dict__:
        form.date_started.data = book_user_info.date_started
    #print(form.data)
    return render_template('review_form.html', title=f"bookshelf | New Review | {book['volumeInfo']['title']}", form=form, book=book, rating=int(rating))

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
        # -- UPDATE --
        # firestore.set_document(f"users/{data['uid']}/books/{data['bid']}", data)
        # -- END UPDATE --

        #print(session['_user']['uid'])
        book = Book(data)
        book.write_to_db()
        
    except Exception as e:
        #print(e)
        resp = jsonify({'status': 'unable to process request'})
    else:
        resp = jsonify({'status': 'success', 'startDate': book.date_started.strftime('%m/%d/%y')})
    return resp
