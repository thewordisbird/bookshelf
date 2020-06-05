from flask import Flask, Blueprint, render_template, request

from .forms import SearchForm
from .google_books import get_book

bp = Blueprint('books', __name__)

@bp.route('/search', methods=["GET"])
def search():
    form = SearchForm()
    return render_template('search.html', title='Find A Book', form=form)


