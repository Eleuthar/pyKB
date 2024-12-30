from core import qpp
from flask import render_template


@qpp.route('/')
@qpp.route('/index')
def index():
    user = {'username': 'qvq'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user)