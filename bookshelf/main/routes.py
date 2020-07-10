from datetime import datetime

from flask import Blueprint, render_template, redirect, request, \
    jsonify, url_for, session, flash

from .forms import SearchForm, ReviewForm, EditProfileForm

import bookshelf.google_books as google_books
import bookshelf.db_maint as db_maint

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
    """
    Display user profile.

    For active users profile the template allows editing of profile 
    information and reviews.
    """
    user = firestore.get_document(f"users/{user_id}")
    books = firestore.get_collection(f"users/{user_id}/books")
    books_reading = [book for book in books if 'date_rated' not in book]
    books_read = [book for book in books if 'date_rated' in book]
    if user_id == session['_user']['uid']:
        active_user = True
    else:
        active_user = False
    return render_template('profile.html', title=f"bookshelf | {user['display_name']}", \
        user=user, books_reading=books_reading, books_read=books_read, \
            active_user=active_user, user_id=user_id)


@bp.route('/profile/edit/<user_id>', methods=['GET', 'POST'])
@auth.login_required
def edit_profile(user_id):
    # Not Yet Implemented
    auth_user = auth.get_user(user_id)
    data = {'display_name': auth_user.display_name}
    providers = auth_user._data['providerUserInfo']
    email_provider = False
    for provider in providers:
        if provider['providerId'] == 'password':
            email_provider = True
            data['email'] = auth_user.email    
    form = EditProfileForm(data=data)
    if form.validate_on_submit():
        update_data = {}
        if form.data['email'] != '': 
            update_data['email'] = form.data['email']
        if form.data['password'] != '': 
            update_data['password'] = form.data['password']
        if form.data['display_name'] != '': 
            update_data['display_name'] = form.data['display_name'] 
        if email_provider:              
            try:
                # Create new firebase auth user
                auth_user = auth.update_user(user_id, update_data)
            except ValueError as v:
                # Covers Passwords being too short
                flash(v)
            except Exception as e:
                # TODO: Clean up depending on where in process error occured
                print(f'Auth Profile Update Error: {e}')
                flash(e)
            else:
                try:
                    # Add successfully authorized user to firestore db
                    db_user_data = update_data
                    if 'password' in db_user_data:
                        del db_user_data['password']
                    db_user_data['last_updated'] = datetime.now()
                    # Add user to firestore
                    firestore.update_document(f"users/{auth_user.uid}", db_user_data)
                    if 'display_name' in update_data: 
                        db_maint.update_user_data_in_books(auth_user.uid, db_user_data)           
                except Exception as e:
                    # TODO: Clean up depending on where in process error occured
                    print(f'User Database Error: {e}')
                    flash('A problem arouse while trying to update your profile. Please try again.')
            
            # Update session data
            for k,v in session['_user'].items():
                if k in update_data and v != update_data[k]:
                    session['_user'][k] = update_data[k]

        return redirect(url_for('books.profile', user_id=user_id))
    return render_template('edit_profile_form.html', form=form, \
        email_provider=email_provider)


@bp.route('/books/search', methods=['GET'])
def search():
    books= google_books.get_books(request.args.get('q'))
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
    rating=int(request.args.get('rating', 0))
    form = ReviewForm(rating=rating)
    book = google_books.get_book(book_id)
    if form.validate_on_submit():
        data = {
            'uid': session['_user']['uid'],
            'display_name': session['_user']['display_name'],
            'bid': book_id,
            'title': book['volumeInfo']['title'],
            'authors': book['volumeInfo']['authors'],
            'cover_url': book['volumeInfo']['imageLinks']['thumbnail'],
            'date_rated': datetime.now(),
            'last_updated': datetime.now(),
            'rating': int(form.data['rating']),
            'review_title': form.data['review_title'],
            'review_content': form.data['review_content'],
            'date_started': form.data['date_started'],
            'date_finished': form.data['date_finished']
        }
        firestore.set_document(f"users/{data['uid']}/books/{book_id}", data)
        return redirect(url_for('books.book_details', book_id=book_id))

    book_user_info = firestore.get_document(f"users/{session['_user']['uid']}/books/{book_id}")
    if book_user_info and 'date_started' in book_user_info:
        form.date_started.data = book_user_info['date_started']

    return render_template('review_form.html', \
        title=f"bookshelf | New Review | {book['volumeInfo']['title']}", \
            form=form, book=book, rating=rating)


@bp.route('/books/review/edit/<book_id>', methods=['GET', 'POST'])
@auth.login_required
def edit_review(book_id):
    book = google_books.get_book(book_id)
    user_review = firestore.get_document(f"users/{session['_user']['uid']}/books/{book_id}")
    review_data = {
        'rating': user_review['rating'],
        'review_title': user_review['review_title'],
        'review_content': user_review['review_content'],
        'date_started': user_review['date_started'],
        'date_finished': user_review['date_finished']
    }
    form = ReviewForm(data=review_data)
    
    if form.validate_on_submit():
        update_data = {
            'last_updated': datetime.now(),
            'rating': int(form.data['rating']),
            'review_title': form.data['review_title'],
            'review_content': form.data['review_content'],
            'date_started': form.data['date_started'],
            'date_finished': form.data['date_finished']
        }
        firestore.update_document(f"users/{session['_user']['uid']}/books/{book_id}", update_data)
        return redirect(url_for('books.book_details', book_id=book_id))
   
    return render_template('review_form.html', form=form, book=book, \
        rating=user_review['rating'])


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
