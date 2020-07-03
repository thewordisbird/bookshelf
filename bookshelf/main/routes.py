from datetime import datetime

from flask import Blueprint, render_template, redirect, request, \
    jsonify, url_for, session

from .forms import SearchForm, ReviewForm

import bookshelf.google_books as google_books

from bookshelf import firebase
auth = firebase.auth()
firestore = firebase.firestore()

bp = Blueprint('books', __name__)

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@auth.login_required
def index():
    books = firestore.get_collection_group("books", order_by=("last_updated", "DESCENDING"))
    return render_template('index.html', title="bookshelf | home", books=books)


@bp.route('/profile/<user_id>', methods=['GET'])
@auth.login_required
def profile(user_id):
    user = firestore.get_document(f"users/{user_id}")
    books = firestore.get_collection(f"users/{user_id}/books")
    
    if user_id == session['_user']['uid']:
        active_user = True
    else:
        active_user = False

    return render_template('profile.html', title=f"bookshelf | {user['display_name']}", user=user, books=books, active_user=active_user)


@bp.route('/profile/edit/<user_id>', methods=['GET', 'POST'])
@auth.login_required
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


@bp.route('/books/search', methods=['GET'])
def search():
    books= google_books.get_books(request.args.get('q'))['items']
    return render_template('search.html', title='bookshelf | Search', books=books)


@bp.route('/books/<book_id>', methods=['GET'])
@auth.login_required
def book_details(book_id):
    book = google_books.get_book(book_id)
    book_user_info = None
    
    if '_user' in session:
        book_user_info = firestore.get_document(f"users/{session['_user']['uid']}/books/{book_id}")
    
    book_reviews = firestore.get_collection_group("books", filters=[("bid", "==", book_id)])
    return render_template('book_details.html', title=f"bookshelf | {book['volumeInfo']['title']}", \
        book=book, book_user_info=book_user_info, book_reviews=book_reviews)


@bp.route('/books/review/new/<book_id>', methods=['GET', 'POST'])
@auth.login_required
def new_review(book_id):
    rating=request.args.get('rating', 0)
    form = ReviewForm(rating=rating)
    book = google_books.get_book(book_id)
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
            'date_rated': datetime.now(),
            'last_updated': datetime.now()
        }
        data.update(form.data)
        book = firestore.set_document(f"users/{data['uid']}/books/{data['bid']}", data)
        return redirect(url_for('books.book_details', book_id=book_id))

    book_user_info = Book.build_from_db(session['_user']['uid'], book_id)

    if 'date_started' in book_user_info.__dict__:
        form.date_started.data = book_user_info.date_started

    return render_template('review_form.html', \
        title=f"bookshelf | New Review | {book['volumeInfo']['title']}", \
            form=form, book=book, rating=int(rating))


@bp.route('/reading', methods=['POST'])
def reading():
    request_data = request.get_json()
    book_id = request_data['bookId']
    
    book = google_books.get_book(book_id)

    data = {
        'uid': session['_user']['uid'],
        'display_name': session['_user']['display_name'],
        'bid': book_id,
        'title': book['volumeInfo']['title'],
        'authors': book['volumeInfo']['authors'],
        'cover_url': book['volumeInfo']['imageLinks']['thumbnail'],
        'date_started': datetime.now(),
        'last_updated': datetime.now()
    }
    try:
        firestore.set_document(f"users/{data['uid']}/books/{data['bid']}", data)
    except Exception as e:
        print(f'Unable To Process Request: {e}')
        resp = jsonify({'status': 'unable to process request'})
    else:
        resp = jsonify({'status': 'success', 'startDate': data['date_started'].strftime('%m/%d/%y')})
    return resp
